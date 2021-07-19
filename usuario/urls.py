from django.urls import path

from . import views

app_name = 'usuario'
urlpatterns = [
    path('', views.historial, name='historial'),
    path('cargar/', views.cargar_db, name='cargarDB'),
    path('lista/', views.lista_usuarios, name='lista'),
    path('lista/<int:id>/', views.editar_usuario, name='detalle'),
    path('fetch', views.fetch_usuarios, name='fetch-usuarios')
]
