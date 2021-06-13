from django.urls import path

from . import views
from estacionamiento.views import historial_estacionamiento

app_name = 'menu_estacionamiento'
urlpatterns = [
    path('menu_estacionamiento/', views.menu_estacionamiento, name='menu_estacionamiento'),
    path('calendario/', views.seleccionar_calendario, name='seleccionarCalendario'),
    path('resumen_tiempo/', views.resumen_tiempo_real, name='resumenTiempoReal'),
    path('proveedores/', views.proveedores, name='proveedores'),
    path('socios/', views.lista_usuarios, name='lista_socios'),
    path('historial/', historial_estacionamiento, name='historial'),
    path('historialCajas/', views.historial_cajas, name='historialCajas'),
    path('tarifaEspecial/', views.tarifas_especiales, name='tarifaEspecial'),
    path('playground/', views.playground, name='playground')
]
