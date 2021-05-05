from django.urls import path
from . import views

app_name = 'estacionamiento'
urlpatterns = [
    path('', views.respuesta, name='registro'),
    path('historial/', views.historial_estacionamiento, name='historial'),
    path('historial/<int:id>/', views.detalle_estacionamiento, name='detalle'),
    path('apertura-manual/', views.apertura_Manual, name='apertura-manual'),
    path('historial/<int:id>/editar/', views.editar_estacionamiento,
         name='editar'),
    path('emision-resumen/', views.emision_resumen_mensual,
         name='resumen-mensual'),
    path('cierre-caja/', views.cierre_caja, name='cierre-caja'),
    path('fetch/', views.fetch_proveedores, name='fetch-proveedores'),
    path('proveedor/add/', views.add_proveedor, name='agregar-proveedor'),
    path('proveedor/<int:id>/', views.detalle_proveedor,
         name='detalle-proveedor'),
    path('proveedor/<int:id>/editar', views.editar_proveedor,
         name='editar-proveedor'),
    path('pago_deuda/<int:id>/', views.pago_deuda, name='pago_deuda'),
    path('fetch_Events',
          views.fetch_Events, name='fetch_Events'),
]
