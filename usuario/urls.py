from django.urls import path
from . import views

app_name= 'usuario'
urlpatterns = [
    path('', views.historial, name='historial'),
    path('cargar/', views.cargarDB, name='cargarDB'),
    path('lista/', views.listaUsuarios, name='lista'),
    path('lista/<int:id>/', views.editarUsuario, name='detalle')
]
