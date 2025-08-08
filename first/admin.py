from django.contrib import admin
from .models import Ciudad, Usuario, Proveedor, Maquina, Producto, Compra, DetalleCompra, Stock, RecargaMaquina

# Register your models here.

@admin.register(Ciudad)
class CiudadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codPostal']
    search_fields = ['nombre', 'codPostal']
    list_filter = ['nombre']

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellido', 'dni', 'telefono', 'is_active']
    search_fields = ['nombre', 'apellido', 'dni']
    list_filter = ['is_active']
    readonly_fields = ['password']
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido', 'dni', 'telefono')
        }),
        ('Autenticación', {
            'fields': ('password', 'is_active'),
            'description': 'La contraseña se hashea automáticamente al guardar'
        }),
    )

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'telefono', 'email']
    search_fields = ['nombre', 'email']
    list_filter = ['nombre']

@admin.register(Maquina)
class MaquinaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ubicacion']
    search_fields = ['nombre', 'ubicacion']
    list_filter = ['ubicacion']

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'marca', 'precioUnitario']
    search_fields = ['nombre', 'marca']
    list_filter = ['marca']
    list_editable = ['precioUnitario']

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ['id', 'fechaHora', 'lugar', 'usuarioEncargado', 'proveedor']
    list_filter = ['fechaHora', 'lugar', 'proveedor']
    search_fields = ['usuarioEncargado__nombre', 'proveedor__nombre']
    readonly_fields = ['fechaHora']

@admin.register(DetalleCompra)
class DetalleCompraAdmin(admin.ModelAdmin):
    list_display = ['compra', 'producto', 'cantidad', 'subtotal']
    list_filter = ['producto', 'compra__fechaHora']
    search_fields = ['producto__nombre', 'compra__id']
    readonly_fields = ['subtotal']

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['producto', 'cantidadDisponible']
    search_fields = ['producto__nombre']
    list_filter = ['producto__marca']
    readonly_fields = ['producto']

@admin.register(RecargaMaquina)
class RecargaMaquinaAdmin(admin.ModelAdmin):
    list_display = ['id', 'fechaHora', 'maquina', 'producto', 'cantidad', 'usuarioResponsable']
    list_filter = ['fechaHora', 'maquina', 'producto']
    search_fields = ['maquina__nombre', 'producto__nombre', 'usuarioResponsable__nombre']
    readonly_fields = ['fechaHora']
