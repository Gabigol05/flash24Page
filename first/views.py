from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Maquina, Producto, Usuario, Stock, RecargaMaquina

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
    return render(request, 'registrarCompra.html')

@require_auth
def actualizarStock(request):
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            maquina_id = request.POST.get('maquina')
            producto_id = request.POST.get('producto')
            cantidad = int(request.POST.get('cantidad'))
            usuario_id = request.POST.get('usuario')
            
            # Validar que todos los campos estén presentes
            if not all([maquina_id, producto_id, cantidad, usuario_id]):
                messages.error(request, '❌ Todos los campos son obligatorios')
                return redirect('actualizarStock')
            
            # Obtener las instancias de los modelos
            maquina = Maquina.objects.get(idMaquina=maquina_id)
            producto = Producto.objects.get(id=producto_id)
            usuario = Usuario.objects.get(idUsuario=usuario_id)
            
            # Verificar si hay stock suficiente
            try:
                stock = Stock.objects.get(producto=producto)
                if not stock.hay_stock_suficiente(cantidad):
                    messages.error(request, f'❌ Stock insuficiente. Disponible: {stock.cantidadDisponible}, Solicitado: {cantidad}')
                    return redirect('actualizarStock')
            except Stock.DoesNotExist:
                messages.error(request, f'❌ No existe stock para el producto {producto.nombre}')
                return redirect('actualizarStock')
            
            # Crear la recarga (esto automáticamente reducirá el stock)
            recarga = RecargaMaquina.objects.create(
                maquina=maquina,
                producto=producto,
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
    context = {
        'maquinas': Maquina.objects.all(),
        'productos': Producto.objects.all(),
        'usuarios': Usuario.objects.all(),
    }
    
    # Agregar información de stock a los productos
    for producto in context['productos']:
        try:
            producto.stock = Stock.objects.get(producto=producto)
        except Stock.DoesNotExist:
            producto.stock = None
    
    return render(request, 'actualizarStock.html', context)