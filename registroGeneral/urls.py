from django.urls import path

from . import views

app_name = "registroGeneral"
urlpatterns = [
    path('', views.respuesta, name='general'),
    path('registro', views.registro, name='registro'),
    path('registro/socio', views.registro_socio, name='registro-socio'),
    path('registro/nosocio', views.registro_nosocio, name='registro-nosocio'),
    path('descargar', views.downloadHistory, name='descargar-historial'),
]

