from django.urls import path
from . import views

app_name = 'draganddrop'
urlpatterns = [
    path('upload/', views.upload, name='upload')
]
