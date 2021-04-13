#menu_estacionamiento/models.py
from django.db import models
from django.urls import reverse

#Example Huiwen Calendar

class Tarifa_mod(models.Model):
    title = models.CharField(max_length=200)
    value = models.FloatField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('menu_estacionamiento:tarifa-detalles', args=(self.id,))

    @property
    def get_html_url(self):
        url = reverse('menu_estacionamiento:tarifa-detalles', args=(self.id,))
        return f'<a href="{url}"> {self.title} </a>'