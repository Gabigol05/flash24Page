from django.urls import path
from . import views

urlpatterns = [
    path('main', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registrarCompra', views.registrarCompra, name='registrarCompra'),
    path('actualizarStock', views.actualizarStock, name='actualizarStock'),
    path('consultarStock', views.consultarStock, name='consultarStock'),
    #Que diga api/... es que solo devuelve datos (JSON), no renderiza plantillas como lo hacen consultarStock o actualizarStock
    path('api/crear-producto-rapido/', views.crear_producto_rapido, name='crear_producto_rapido'),
]