from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# Create your models here.

class Ciudad(models.Model):
    nombre = models.CharField(max_length=100)
    codPostal = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return self.nombre

class Usuario(models.Model):
    nombre = models.CharField(max_length=200)
    apellido = models.CharField(max_length=200)
    dni = models.IntegerField(unique=True)
    idUsuario = models.AutoField(primary_key=True)
    telefono = models.CharField(max_length=20)
    # Campos para autenticación
    password = models.CharField(max_length=128, default='')
    is_active = models.BooleanField(default=True)
    
    def set_password(self, raw_password):
        """Establece la contraseña hasheada"""
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Verifica si la contraseña es correcta"""
        return check_password(raw_password, self.password)
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Proveedor(models.Model):
    nombre = models.CharField(max_length=200)
    idProveedor = models.AutoField(primary_key=True)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(max_length=200)
    
    def __str__(self):
        return self.nombre

class Maquina(models.Model):
    idMaquina = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    ubicacion = models.CharField(max_length=200)
    
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    marca = models.CharField(max_length=100)
    precioUnitario = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.nombre} - {self.marca}"

class Compra(models.Model):
    fechaHora = models.DateTimeField(auto_now_add=True)
    lugar = models.ForeignKey(Ciudad, on_delete=models.CASCADE, related_name='compras')
    usuarioEncargado = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='compras')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='compras')
    
    def __str__(self):
        return f"Compra {self.id} - {self.fechaHora.strftime('%d/%m/%Y %H:%M')}"
    
    class Meta:
        ordering = ['-fechaHora']

class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='detalles_compra')
    cantidad = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        # Calcular automáticamente el subtotal
        self.subtotal = self.producto.precioUnitario * self.cantidad
        
        # Verificar si es una nueva instancia (creación) o actualización
        is_new = self.pk is None
        
        # Guardar el detalle de compra
        super().save(*args, **kwargs)
        
        # Si es una nueva compra, actualizar el stock
        if is_new:
            self.actualizar_stock_producto()
    
    def actualizar_stock_producto(self):
        """Actualiza el stock del producto cuando se registra una compra"""
        try:
            # Obtener o crear el stock del producto
            stock, created = Stock.objects.get_or_create(
                producto=self.producto,
                defaults={'cantidadDisponible': 0}
            )
            
            # Aumentar el stock con la cantidad comprada
            stock.actualizar_stock(self.cantidad)
            
        except Exception as e:
            # En caso de error, podrías logearlo
            print(f"Error al actualizar stock: {e}")
    
    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} - ${self.subtotal}"

class Stock(models.Model):
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE, primary_key=True)
    cantidadDisponible = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Stock de {self.producto.nombre}: {self.cantidadDisponible} unidades"
    
    def actualizar_stock(self, cantidad):
        """Actualiza el stock del producto (aumenta)"""
        self.cantidadDisponible += cantidad
        self.save()
    
    def reducir_stock(self, cantidad):
        """Reduce el stock del producto (venta)"""
        if self.cantidadDisponible >= cantidad:
            self.cantidadDisponible -= cantidad
            self.save()
            return True
        return False
    
    def hay_stock_suficiente(self, cantidad):
        """Verifica si hay stock suficiente para una cantidad específica"""
        return self.cantidadDisponible >= cantidad
    
    def stock_bajo(self, umbral=10):
        """Verifica si el stock está por debajo del umbral"""
        return self.cantidadDisponible <= umbral
    
    def porcentaje_stock(self):
        """Retorna el porcentaje de stock disponible (para inventario)"""
        # Puedes definir un stock máximo según tus necesidades
        stock_maximo = 100  # Ejemplo
        return (self.cantidadDisponible / stock_maximo) * 100

class RecargaMaquina(models.Model):
    """Modelo para registrar las recargas de máquinas expendedoras"""
    fechaHora = models.DateTimeField(auto_now_add=True)
    maquina = models.ForeignKey(Maquina, on_delete=models.CASCADE, related_name='recargas')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='recargas')
    cantidad = models.IntegerField()
    usuarioResponsable = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='recargas_realizadas')
    
    def save(self, *args, **kwargs):
        # Verificar si es una nueva instancia
        is_new = self.pk is None
        
        # Guardar la recarga
        super().save(*args, **kwargs)
        
        # Si es una nueva recarga, reducir el stock
        if is_new:
            self.reducir_stock_producto()
    
    def reducir_stock_producto(self):
        """Reduce el stock del producto cuando se recarga una máquina"""
        try:
            # Obtener el stock del producto
            stock = Stock.objects.get(producto=self.producto)
            
            # Verificar si hay stock suficiente
            if stock.hay_stock_suficiente(self.cantidad):
                # Reducir el stock
                stock.reducir_stock(self.cantidad)
                return True
            else:
                # Si no hay stock suficiente, eliminar la recarga
                self.delete()
                raise ValueError(f"No hay stock suficiente. Disponible: {stock.cantidadDisponible}, Solicitado: {self.cantidad}")
                
        except Stock.DoesNotExist:
            # Si no existe stock, eliminar la recarga
            self.delete()
            raise ValueError(f"No existe stock para el producto {self.producto.nombre}")
        except Exception as e:
            print(f"Error al reducir stock: {e}")
            return False
    
    def __str__(self):
        return f"Recarga {self.id} - {self.maquina.nombre}: {self.cantidad}x {self.producto.nombre}"
    
    class Meta:
        ordering = ['-fechaHora']
    


