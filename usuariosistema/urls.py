from django.urls import path
from . import views

app_name = 'usuariosistema'
urlpatterns = [
    path('', views.home, name='home'),
    path('cambiarContrasena/', views.cambiarContrasena, name = 'cambiarContrasena'),
    path('registro/', views.registro, name='registro'),
    path('logoutSis/',views.logout, name = 'logout'),
]
