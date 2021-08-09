from django.urls import path

from . import views

app_name = 'estacionamiento'
urlpatterns = [
    path('', views.respuesta, name='registro'),
    path('apertura-manual/', views.apertura_manual, name='apertura-manual'),
    path('historial/', views.historial_estacionamiento, name='historial'),
    path('historial/<int:id>/detalle/<str:origen>', views.detalle_estacionamiento, name='detalle'),
    path('historial/<int:id>/editar/<str:origen>', views.editar_estacionamiento, name='editar'),
    path('historial/<int:id>/detalle/<str:origen>/cobrarEntrada', views.cobrar_entrada, name='cobrarEntrada'),
    path('historial/<int:id>/gen-pdf/<str:origen>', views.generate_pdf, name='gen-pdf'),
    path('historial/<int:id>/pago_deuda', views.pago_deuda, name='pago_deuda'),
    path('emision-resumen/', views.emision_resumen_mensual, name='resumen-mensual'),
    path('emision-resumen-get/', views.emision_resumen_mensual_get, name='resumen-mensual-get'),
    path('cierre-caja/', views.cierre_caja, name='cierre-caja'),
    path('proveedor/add/', views.add_proveedor, name='agregar-proveedor'),
    path('proveedor/<int:id>/', views.detalle_proveedor, name='detalle-proveedor'),
    path('proveedor/<int:id>/editar', views.editar_proveedor, name='editar-proveedor'),
    path('proveedor/fetch/', views.fetch_proveedores, name='fetch-proveedores'),
    path('fetch_Events', views.fetch_events, name='fetch_Events'),
    path('emision_resumen/<int:id>/', views.emision_resumen_anterior, name='emision_anterior')
]
