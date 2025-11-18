from django.urls import path
from . import views

urlpatterns = [
    path('main', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registrarCompra', views.registrarCompra, name='registrarCompra'),
    path('actualizarStock', views.actualizarStock, name='actualizarStock'),
    path('consultarStock', views.consultarStock, name='consultarStock'),
]