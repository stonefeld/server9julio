from django.urls import path
from . import views

app_name = 'usuariosistema'
urlpatterns = [
    path('', views.home, name='home'),
    path('registro/', views.registro, name='registro'),
]
