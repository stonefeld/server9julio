from django.urls import path, include
from . import views

app_name='menu_estacionamiento'
urlpatterns = [
    path('menu_estacionamiento/', views.menu_estacionamiento, name='menu_estacionamiento'),#respuesta/
    path('calendario/', views.seleccionarCalendario, name='seleccionarCalendario'),
    path('resumen_tiempo', views.resumenTiempoReal, name='resumenTiempoReal'),
    path('proveedores', views.proveedores, name='proveedores'),
    path('historial', views.historial, name='historial'),
]