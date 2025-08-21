from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Maquina, Producto, Usuario, StockCiudad, RecargaMaquina, Proveedor, Ciudad, Compra, DetalleCompra

# Create your views here.

def login_view(request):
    """Vista para el login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            # Buscar usuario por DNI (como username)
            usuario = Usuario.objects.get(dni=username, is_active=True)
            
            # Verificar contraseña
            if usuario.check_password(password):
                # Guardar usuario en sesión
                request.session['user_id'] = usuario.idUsuario
                request.session['user_name'] = f"{usuario.nombre} {usuario.apellido}"
                return redirect('index')
            else:
                return render(request, 'login.html', {
                    'error_message': '❌ Usuario o contraseña incorrectos'
                })
        except Usuario.DoesNotExist:
            return render(request, 'login.html', {
                'error_message': '❌ Usuario o contraseña incorrectos'
            })
    
    return render(request, 'login.html')

def logout_view(request):
    """Vista para el logout"""
    # Limpiar sesión
    request.session.flush()
    return redirect('login')

def is_authenticated(request):
    """Verificar si el usuario está autenticado"""
    return 'user_id' in request.session

def require_auth(view_func):
    """Decorador para proteger vistas"""
    def wrapper(request, *args, **kwargs):
        if not is_authenticated(request):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

@require_auth
def index(request):
    return render(request, 'index.html')

@require_auth
def registrarCompra(request):
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            proveedor_id = request.POST.get('proveedor')
            lugar_id = request.POST.get('lugar')
            importe_total = float(request.POST.get('importe_total'))
            
            # Validar que todos los campos estén presentes
            if not all([proveedor_id, lugar_id, importe_total]):
                messages.error(request, '❌ Todos los campos son obligatorios')
                return redirect('registrarCompra')
            
            # Obtener las instancias de los modelos
            proveedor = Proveedor.objects.get(idProveedor=proveedor_id)
            lugar = Ciudad.objects.get(id=lugar_id)
            usuario = Usuario.objects.get(idUsuario=request.session['user_id'])
            
            # Crear la compra
            compra = Compra.objects.create(
                lugar=lugar,
                usuarioEncargado=usuario,
                proveedor=proveedor
            )
            
            # Procesar detalles de la compra
            total_calculado = 0
            detalles_procesados = 0
            
            # Obtener todos los campos del formulario
            for key, value in request.POST.items():
                if key.startswith('producto_') and value:
                    detalle_num = key.split('_')[1]
                    producto_id = value
                    cantidad = int(request.POST.get(f'cantidad_{detalle_num}', 0))
                    precio_unitario = float(request.POST.get(f'precio_unitario_{detalle_num}', 0))
                    subtotal = float(request.POST.get(f'subtotal_{detalle_num}', 0))
                    
                    if producto_id and cantidad > 0 and precio_unitario > 0:
                        producto = Producto.objects.get(id=producto_id)
                        
                        # Crear el detalle de compra
                        DetalleCompra.objects.create(
                            compra=compra,
                            producto=producto,
                            cantidad=cantidad,
                            subtotal=subtotal
                        )
                        
                        total_calculado += subtotal
                        detalles_procesados += 1
            
            # Validar que el importe total coincida con la suma de los detalles
            if abs(importe_total - total_calculado) > 0.01:
                # Si no coincide, eliminar la compra y mostrar error
                compra.delete()
                messages.error(request, f'❌ El importe total (${importe_total}) no coincide con la suma de los detalles (${total_calculado:.2f})')
                return redirect('registrarCompra')
            
            if detalles_procesados == 0:
                compra.delete()
                messages.error(request, '❌ Debe agregar al menos un producto a la compra')
                return redirect('registrarCompra')
            
            messages.success(request, f'✅ Compra registrada exitosamente: {detalles_procesados} productos por ${total_calculado:.2f}')
            return redirect('registrarCompra')
            
        except (Proveedor.DoesNotExist, Ciudad.DoesNotExist, Producto.DoesNotExist) as e:
            messages.error(request, f'❌ Error: {str(e)}')
            return redirect('registrarCompra')
        except ValueError as e:
            messages.error(request, f'❌ Error de validación: {str(e)}')
            return redirect('registrarCompra')
        except Exception as e:
            messages.error(request, f'❌ Error inesperado: {str(e)}')
            return redirect('registrarCompra')
    
    # GET request - mostrar el formulario
    import json
    
    context = {
        'proveedores': Proveedor.objects.all(),
        'ciudades': Ciudad.objects.all(),
        'productos': Producto.objects.all(),
    }
    
    # Convertir productos a JSON para JavaScript
    productos_json = []
    for producto in context['productos']:
        productos_json.append({
            'id': producto.id,
            'nombre': producto.nombre,
            'marca': producto.marca,
            'precioUnitario': float(producto.precioUnitario)
        })
    
    context['productos_json'] = json.dumps(productos_json)
    
    return render(request, 'registrarCompra.html', context)

@require_auth
def actualizarStock(request):
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            maquina_id = request.POST.get('maquina')
            producto_id = request.POST.get('producto')
            cantidad = int(request.POST.get('cantidad'))
            usuario_id = request.POST.get('usuario')
            ciudad_id = request.POST.get('ciudad')

            # Validar que todos los campos estén presentes
            if not all([maquina_id, producto_id, cantidad, usuario_id, ciudad_id]):
                messages.error(request, '❌ Todos los campos son obligatorios')
                return redirect('actualizarStock')

            # Obtener las instancias de los modelos
            maquina = Maquina.objects.get(idMaquina=maquina_id)
            producto = Producto.objects.get(id=producto_id)
            usuario = Usuario.objects.get(idUsuario=usuario_id)
            ciudad = Ciudad.objects.get(id=ciudad_id)

            # Verificar si hay stock suficiente
            try:
                stock = StockCiudad.objects.get(producto=producto, ciudad=ciudad)
                if not stock.hay_stock_suficiente(cantidad):
                    messages.error(request, f'❌ Stock insuficiente. Disponible: {stock.cantidadDisponible}, Solicitado: {cantidad}')
                    return redirect('actualizarStock')
            except StockCiudad.DoesNotExist:
                messages.error(request, f'❌ No existe stock para el producto {producto.nombre} en {ciudad.nombre}')
                return redirect('actualizarStock')

            # Crear la recarga (esto automáticamente reducirá el stock)
            recarga = RecargaMaquina.objects.create(
                maquina=maquina,
                producto=producto,
                ciudad=ciudad,
                cantidad=cantidad,
                usuarioResponsable=usuario
            )
            
            messages.success(request, f'✅ Recarga registrada exitosamente: {cantidad} unidades de {producto.nombre} en {maquina.nombre}')
            return redirect('actualizarStock')
            
        except (Maquina.DoesNotExist, Producto.DoesNotExist, Usuario.DoesNotExist) as e:
            messages.error(request, f'❌ Error: {str(e)}')
            return redirect('actualizarStock')
        except ValueError as e:
            messages.error(request, f'❌ Error de validación: {str(e)}')
            return redirect('actualizarStock')
        except Exception as e:
            messages.error(request, f'❌ Error inesperado: {str(e)}')
            return redirect('actualizarStock')
    
    # GET request - mostrar el formulario
    ciudad_id = request.GET.get('ciudad')
    ciudad = Ciudad.objects.filter(id=ciudad_id).first()

    context = {
        'maquinas': Maquina.objects.all(),
        'productos': Producto.objects.all(),
        'usuarios': Usuario.objects.all(),
        'ciudades': Ciudad.objects.all(),
        'ciudad_seleccionada': int(ciudad_id) if ciudad else None,
    }

    for producto in context['productos']:
        if ciudad:
            producto.stock = StockCiudad.objects.filter(producto=producto, ciudad=ciudad).first()
        else:
            producto.stock = None

    return render(request, 'actualizarStock.html', context)

@require_auth
def consultarStock(request):
    ciudad_id = request.GET.get('ciudad')
    ciudad = Ciudad.objects.filter(id=ciudad_id).first()

    productos = Producto.objects.all()
    for producto in productos:
        if ciudad:
            producto.stock = StockCiudad.objects.filter(producto=producto, ciudad=ciudad).first()
        else:
            producto.stock = None

    context = {
        'productos': productos,
        'ciudades': Ciudad.objects.all(),
        'ciudad_seleccionada': int(ciudad_id) if ciudad else None,
    }

    return render(request, 'consultarStock.html', context)
