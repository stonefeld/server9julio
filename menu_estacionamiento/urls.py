from django.urls import path, include
from . import views

app_name='menu_estacionamiento'
urlpatterns = [
    path('menu_estacionamiento/', views.menu_estacionamiento, name='menu_estacionamiento'),#respuesta/
    path('calendario/', views.CalendarView.as_view(), name='calendario'),
    path('tarifa/nueva/', views.tarifa, name='tarifa_nueva'),

    path('tarifa/editar/<int:pk>/', views.TarifaEdit.as_view(), name='tarida_editar'), #editar
    path('tarifa/<int:tarifa_id>/detalles/', views.tarifa_detalles, name='tarifa-detalles'), #el que haces cliclk
    
    #path('tarifa/editar/<int:event_id>/', views.tarifa, name='tarifa_editar'),
    path('resumen_tiempo/', views.resumenTiempoReal, name='resumenTiempoReal'),
    path('proveedores/', views.proveedores, name='proveedores'),
    path('historial/', views.historial, name='historial'),
]