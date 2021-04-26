from django.urls import path

from . import views
from estacionamiento.views import historial_estacionamiento

app_name = 'menu_estacionamiento'
urlpatterns = [
    path('menu_estacionamiento/',
         views.menu_estacionamiento,
         name='menu_estacionamiento'),
    path('calendario/',
         views.seleccionarCalendario,
         name='seleccionarCalendario'),
    path('resumen_tiempo', views.resumenTiempoReal, name='resumenTiempoReal'),
    path('proveedores', views.proveedores, name='proveedores'),
    path('historial', historial_estacionamiento, name='historial'),
]
