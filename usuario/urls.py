from django.urls import path
from . import views

app_name = 'usuario'
urlpatterns = [
    path('', views.respuesta, name='entrada-respuesta'),
]
