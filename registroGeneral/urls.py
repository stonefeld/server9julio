from django.urls import path

from . import views

app_name = 'registroGeneral'
urlpatterns = [
    path('', views.respuesta, name='general'),
    path('registro', views.registro, name='registro'),
    path('registro/socio', views.registro_socio, name='registro-socio'),
    path('registro/nosocio', views.registro_nosocio, name='registro-nosocio'),
    path('descargar', views.cargar_historial, name='descargar-historial'),
    path('lista', views.lista_historiales, name='lista-historial'),
    path('borrar-historial', views.borrar_historial, name='borrar-historial'),
]
