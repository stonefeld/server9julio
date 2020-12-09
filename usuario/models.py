from django.db import models
from django.utils import timezone

class Persona(models.Model):
    nrTarjeta = models.IntegerField( null=False, blank=False, verbose_name='Nr. de Tarjeta')
    nombre_apellido = models.CharField(max_length=30, verbose_name='Nombre y Apellido')
    dni = models.IntegerField(verbose_name='DNI')
    nrSocio = models.IntegerField(null=True, blank=True, verbose_name='Nr. de Socio')
    general = models.BooleanField(default=False)
    pileta = models.BooleanField(default=False)
    tenis = models.BooleanField(default=False)
    deuda = models.FloatField(null=True)

    def __str__(self):
        return str(self.nombre_apellido)
    
    def get_absolute_url(self):
        return f"/usuario/tarjetas/{self.id}/"

class Deuda(models.Model):
    deuda = models.FloatField()

