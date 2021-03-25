from django.db import models


class Persona(models.Model):
    nombre_apellido = models.CharField(max_length=30, verbose_name='Nombre y Apellido')
    dni = models.IntegerField(null=True, verbose_name='DNI')
    nrTarjeta = models.IntegerField(null=True, blank=True, verbose_name='Nr. de Tarjeta')
    nrSocio = models.IntegerField(null=True, blank=True, verbose_name='Nr. de Socio')
    general = models.BooleanField(default=False, verbose_name='General')
    pileta = models.BooleanField(default=False, verbose_name='Pileta')
    tenis = models.BooleanField(default=False, verbose_name='Tenis')
    deuda = models.FloatField(null=True, verbose_name='Deuda', default=0)

    def __str__(self):
        return str(self.nombre_apellido)

    def get_absolute_url(self):
        return f'/usuario/lista/{self.id}/'


class Deuda(models.Model):
    deuda = models.FloatField(default=300)
