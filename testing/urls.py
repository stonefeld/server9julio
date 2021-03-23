from django.urls import path
from . import views

app_name = 'estacionamiento'
urlpatterns = [
    path('', views.inicio, name='testing'),
]