from django.core.management.base import BaseCommand
from first.models import Ciudad, Usuario, Proveedor, Maquina, Producto, Stock

class Command(BaseCommand):
    help = 'Pobla la base de datos con datos de ejemplo para el sistema de máquinas expendedoras'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Poblando base de datos con datos de ejemplo...')
        
        # Crear ciudades
        ciudades = [
            {'nombre': 'Buenos Aires', 'codPostal': '1000'},
            {'nombre': 'Córdoba', 'codPostal': '5000'},
            {'nombre': 'Rosario', 'codPostal': '2000'},
            {'nombre': 'Mendoza', 'codPostal': '5500'},
        ]
        
        for ciudad_data in ciudades:
            ciudad, created = Ciudad.objects.get_or_create(
                codPostal=ciudad_data['codPostal'],
                defaults=ciudad_data
            )
            if created:
                self.stdout.write(f'✅ Ciudad creada: {ciudad.nombre}')
        
        # Crear usuarios
        usuarios = [
            {'nombre': 'Juan', 'apellido': 'Pérez', 'dni': 12345678, 'telefono': '11-1234-5678'},
            {'nombre': 'María', 'apellido': 'González', 'dni': 23456789, 'telefono': '11-2345-6789'},
            {'nombre': 'Carlos', 'apellido': 'López', 'dni': 34567890, 'telefono': '11-3456-7890'},
            {'nombre': 'Ana', 'apellido': 'Martínez', 'dni': 45678901, 'telefono': '11-4567-8901'},
        ]
        
        for usuario_data in usuarios:
            usuario, created = Usuario.objects.get_or_create(
                dni=usuario_data['dni'],
                defaults=usuario_data
            )
            if created:
                self.stdout.write(f'✅ Usuario creado: {usuario.nombre} {usuario.apellido}')
        
        # Crear proveedores
        proveedores = [
            {'nombre': 'Distribuidora Central', 'telefono': '11-1111-1111', 'email': 'central@dist.com'},
            {'nombre': 'Proveedor Express', 'telefono': '11-2222-2222', 'email': 'express@prov.com'},
            {'nombre': 'Suministros Rápidos', 'telefono': '11-3333-3333', 'email': 'rapidos@sum.com'},
        ]
        
        for proveedor_data in proveedores:
            proveedor, created = Proveedor.objects.get_or_create(
                email=proveedor_data['email'],
                defaults=proveedor_data
            )
            if created:
                self.stdout.write(f'✅ Proveedor creado: {proveedor.nombre}')
        
        # Crear máquinas
        maquinas = [
            {'nombre': 'Máquina A', 'ubicacion': 'Planta Baja - Recepción'},
            {'nombre': 'Máquina B', 'ubicacion': 'Primer Piso - Cafetería'},
            {'nombre': 'Máquina C', 'ubicacion': 'Segundo Piso - Oficinas'},
            {'nombre': 'Máquina D', 'ubicacion': 'Sótano - Gimnasio'},
        ]
        
        for maquina_data in maquinas:
            maquina, created = Maquina.objects.get_or_create(
                nombre=maquina_data['nombre'],
                defaults=maquina_data
            )
            if created:
                self.stdout.write(f'✅ Máquina creada: {maquina.nombre}')
        
        # Crear productos
        productos = [
            {'nombre': 'Coca Cola', 'marca': 'Coca-Cola', 'precioUnitario': 2.50},
            {'nombre': 'Pepsi', 'marca': 'PepsiCo', 'precioUnitario': 2.30},
            {'nombre': 'Agua Mineral', 'marca': 'Villavicencio', 'precioUnitario': 1.80},
            {'nombre': 'Cerveza', 'marca': 'Quilmes', 'precioUnitario': 3.50},
            {'nombre': 'Snack Doritos', 'marca': 'Frito-Lay', 'precioUnitario': 4.20},
            {'nombre': 'Chocolate KitKat', 'marca': 'Nestlé', 'precioUnitario': 3.80},
            {'nombre': 'Galletas Oreo', 'marca': 'Mondelez', 'precioUnitario': 4.50},
            {'nombre': 'Café', 'marca': 'La Virginia', 'precioUnitario': 2.00},
        ]
        
        for producto_data in productos:
            producto, created = Producto.objects.get_or_create(
                nombre=producto_data['nombre'],
                marca=producto_data['marca'],
                defaults=producto_data
            )
            if created:
                self.stdout.write(f'✅ Producto creado: {producto.nombre}')
        
        # Crear stock inicial para todos los productos
        for producto in Producto.objects.all():
            stock, created = Stock.objects.get_or_create(
                producto=producto,
                defaults={'cantidadDisponible': 100}  # Stock inicial de 100 unidades
            )
            if created:
                self.stdout.write(f'✅ Stock creado para {producto.nombre}: 100 unidades')
        
        self.stdout.write(self.style.SUCCESS('🎉 ¡Datos de ejemplo creados exitosamente!'))
        self.stdout.write('📊 Resumen:')
        self.stdout.write(f'   - {Ciudad.objects.count()} ciudades')
        self.stdout.write(f'   - {Usuario.objects.count()} usuarios')
        self.stdout.write(f'   - {Proveedor.objects.count()} proveedores')
        self.stdout.write(f'   - {Maquina.objects.count()} máquinas')
        self.stdout.write(f'   - {Producto.objects.count()} productos')
        self.stdout.write(f'   - {Stock.objects.count()} registros de stock') 