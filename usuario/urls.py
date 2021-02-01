from django.urls import path
from . import views

app_name= 'usuario'
urlpatterns = [
    path('', views.historial, name='historial'),
    path('cargar/', views.cargarDB, name='cargarDB'),
    path('tarjetas/', views.listaUsuarios, name='tarjeta'),
    path('tarjetas/<int:id>/', views.editarUsuario, name='vincular')
]
