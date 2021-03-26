from django.urls import path
from . import views

app_name = 'estacionamiento'
urlpatterns = [
    path('', views.respuesta, name='registro'),
    path('historial/',
         views.historial_estacionamiento,
         name='historial'),
    path('historial/<int:id>/',
         views.detalle_estacionamiento,
         name='detalle'),
     path('emision_resumen',
          views.emision_resumen_mensual,
          name='resumen-mensual'),
     path('cierre-caja', 
          views.cierre_caja,
          name='cierre-caja')
]
