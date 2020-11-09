from django.urls import path
from . import views

urlpatterns = [
    path('', views.tablaIngresos, name='entrada-respuesta'),#respuesta/
]
