from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Maquina, Producto, Usuario, StockCiudad, RecargaMaquina, Proveedor, Ciudad, Compra, DetalleCompra
import json

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
            # Procesar actualizaciones de precios ANTES de crear la compra
            actualizar_precios_productos(request.POST)

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

def actualizar_precios_productos(post_data):
    """
    Función que busca y actualiza precios modificados
    """
    for key, value in post_data.items():
        # Buscar campos que empiecen con 'nuevo_precio_'
        if key.startswith('nuevo_precio_') and value:
            try:
                # Extraer el ID del producto del nombre del campo
                producto_id = key.split('_')[2]  # nuevo_precio_123 -> 123
                
                # Verificar si este precio realmente cambió
                input_element_changed = post_data.get(f'precio_changed_{producto_id}', False)
                
                if input_element_changed:
                    # Obtener el producto y actualizar su precio
                    producto = Producto.objects.get(id=producto_id)
                    nuevo_precio = float(value)
                    
                    # Validación en backend
                    if nuevo_precio > 0:
                        producto.precioUnitario = nuevo_precio
                        producto.save()
                        
            except (Producto.DoesNotExist, ValueError) as e:
                # Log del error pero no interrumpir el proceso
                print(f"Error actualizando precio: {e}")
                continue

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
        'ciudad': ciudad,  # Agregar la ciudad al contexto
    }

    for producto in context['productos']:
        if ciudad:
            producto.stock = StockCiudad.objects.filter(producto=producto, ciudad=ciudad).first()
        else:
            producto.stock = None

    return render(request, 'actualizarStock.html', context,)

@require_auth
def consultarStock(request):
    ciudad_id = request.GET.get('ciudad')
    ciudad = Ciudad.objects.filter(id=ciudad_id).first()

    productos = Producto.objects.all()
    for producto in productos:
        if ciudad:
            producto.stock = StockCiudad.objects.filter(producto=producto, ciudad=ciudad).first()
            # Verificar alertas para cada producto
            if producto.stock:
                producto.stock.verificar_alertas()
        else:
            producto.stock = None
    
    # Obtener productos con alertas
    alertas_stock = []
    if ciudad:
        alertas_stock = StockCiudad.objects.filter(
            ciudad=ciudad,
            estado_alerta=True
        ).select_related('producto', 'ciudad')

    context = {
        'productos': productos,
        'ciudades': Ciudad.objects.all(),
        'ciudad_seleccionada': int(ciudad_id) if ciudad else None,
        'alertas_stock': alertas_stock,
        'total_alertas': len(alertas_stock),
    }

    return render(request, 'consultarStock.html', context)

@require_auth
def dashboard(request):
    # Obtener productos con alerta
    productos_alerta = StockCiudad.objects.filter(
        estado_alerta=True
    ).select_related('producto', 'ciudad')
    
    # Resto del código del dashboard...
    
    context = {
        'alertas_stock': productos_alerta,
        'total_alertas': productos_alerta.count(),
        # Resto del contexto...
    }
    
    return render(request, 'dashboard.html', context)

@require_auth
def crear_producto_rapido(request):
    try:
        print("Cuerpo recibido:", request.body) 
        print("Tipo de contenido:", request.headers.get('Content-Type'))
        data = json.loads(request.body)
        nombre = data.get('nombre')
        marca = data.get('marca')
        precioUnitario = data.get('precioUnitario')
        
        if not nombre:
            return JsonResponse({'success': False, 'error': 'El nombre es obligatorio'})
        if not marca:
            return JsonResponse({'success': False, 'error': 'La marca es obligatoria'})
        if not precioUnitario:
            return JsonResponse({'success': False, 'error': 'El precio unitario es obligatorio'})
        
        #validaciones adicionales
        palabrasNuevas = set(nombre.lower().split())
        productos_existentes = Producto.objects.values_list('nombre', flat=True)
        for nombre_existente in productos_existentes:
            palabras_existentes = set(nombre_existente.lower().split())

            # Comparamos los conjuntos. Si son iguales, tienen las mismas palabras
            if palabrasNuevas == palabras_existentes:
                return JsonResponse({
                    'success': False, 
                    'error': f'Ya existe un producto similar: "{nombre_existente}"'
                })


        # Crear el producto
        nuevo_producto = Producto.objects.create(
            nombre=nombre,
            marca=marca,
            precioUnitario=precioUnitario,
        )

        return JsonResponse({
            'success': True,
            'id': nuevo_producto.id,
            'nombre': nuevo_producto.nombre,
            'marca': nuevo_producto.marca,
            'precioUnitario': nuevo_producto.precioUnitario
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
@require_auth
def crear_maquinaRapido(request):
    try:
        print("Cuerpo recibido:", request.body) 
        print("Tipo de contenido:", request.headers.get('Content-Type'))
        data = json.loads(request.body)
        nombre = data.get('nombre')
        ubicacion = data.get('ubicacion')
        
        if not nombre:
            return JsonResponse({'success': False, 'error': 'El nombre es obligatorio'})
        if not ubicacion:
            return JsonResponse({'success': False, 'error': 'La ubicacion es obligatoria'})
        
        #validaciones adicionales
        palabrasNuevas = set(nombre.lower().split())
        maquinas_existentes = Maquina.objects.values_list('nombre', flat=True)
        for nombre_existente in maquinas_existentes:
            palabras_existentes = set(nombre_existente.lower().split())

            # Comparamos los conjuntos. Si son iguales, tienen las mismas palabras
            if palabrasNuevas == palabras_existentes:
                return JsonResponse({
                    'success': False, 
                    'error': f'Ya existe una maquina similar: "{nombre_existente}"'
                })


        # Crear la maquina
        nueva_maquina = Maquina.objects.create(
            nombre=nombre,
            ubicacion=ubicacion,
        )

        return JsonResponse({
            'success': True,
            'id': nueva_maquina.id,
            'nombre': nueva_maquina.nombre,
            'ubicacion': nueva_maquina.ubicacion,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_auth
def crear_proveedor_rapido(request):
    try:
        data = json.loads(request.body)
        nombre = data.get('nombre')
        telefono = data.get('telefono')
        email = data.get('email')

        if not nombre:
            return JsonResponse({'success': False, 'error': 'El nombre es obligatorio'})
        if not telefono:
            return JsonResponse({'success': False, 'error': 'El teléfono es obligatorio'})
        if not email:
            return JsonResponse({'success': False, 'error': 'El email es obligatorio'})

        # Validaciones de duplicado básicas
        # 1) Evitar nombres muy similares por coincidencia de palabras
        palabras_nuevas = set(nombre.lower().split())
        proveedores_existentes = Proveedor.objects.values_list('nombre', flat=True)
        for nombre_existente in proveedores_existentes:
            palabras_existentes = set(nombre_existente.lower().split())
            if palabras_nuevas == palabras_existentes:
                return JsonResponse({
                    'success': False,
                    'error': f'Ya existe un proveedor similar: "{nombre_existente}"'
                })

        # 2) Evitar emails duplicados
        if Proveedor.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'error': 'Ya existe un proveedor con ese email'})

        # Crear proveedor
        nuevo_proveedor = Proveedor.objects.create(
            nombre=nombre,
            telefono=telefono,
            email=email,
        )

        return JsonResponse({
            'success': True,
            'idProveedor': nuevo_proveedor.idProveedor,
            'nombre': nuevo_proveedor.nombre,
            'telefono': nuevo_proveedor.telefono,
            'email': nuevo_proveedor.email,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})