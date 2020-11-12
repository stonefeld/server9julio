from django.urls import path
from . import views

urlpatterns = [
    path('', views.respuesta, name='general-respuesta'),
    path('registro', views.registro, name='general-registro'),
]
