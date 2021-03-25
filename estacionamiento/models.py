from django.db import models
from django.utils.timezone import now

from usuario.models import Persona


class Proveedor(models.Model):
    idProveedor = models.CharField(max_length=30, verbose_name='idProveedor')
    nombre_proveedor = models.CharField(max_length=30, verbose_name='Proveedor')

    def __str__(self):
        return str(self.nombre_proveedor)


class RegistroEstacionamiento(models.Model):
    TIPO_CHOICES = (
        ('socio', 'SOCIO'),
        ('socio-moroso', 'SOCIO-MOROSO'),
        ('nosocio', 'NOSOCIO'),
        ('proveedor', 'PROVEEDOR')
    )

    DIRECCION_CHOICES = (
        ('entrada', 'ENTRADA'),
        ('salida', 'SALIDA')
    )

    tipo = models.CharField(max_length=30, verbose_name='Tipo', choices=TIPO_CHOICES, default='SOCIO')
    identificador = models.CharField(max_length=30, verbose_name='Identificador', null=True, blank=True)
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, verbose_name='Persona', null=True, blank=True)
    noSocio = models.IntegerField(verbose_name='DNI', null=True, blank=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, verbose_name='Proveedor', null=True, blank=True)
    lugar = models.CharField(max_length=30, verbose_name='Lugar')
    tiempo = models.DateTimeField(default=now, verbose_name='Fecha y Hora')
    direccion = models.CharField(max_length=30, choices=DIRECCION_CHOICES, verbose_name='Dirección', default='ENTRADA')
    autorizado = models.BooleanField(default=False, verbose_name='Autorización')
    cicloCaja = models.IntegerField(null=True, verbose_name='cicloCaja')
    cicloMensual = models.IntegerField(null=True, verbose_name='cicloMensual')

    def __str__(self):
        return f'{self.tiempo} - {self.identificador}'

    def get_absolute_url(self):
        return f'/estacionamiento/historial/{self.id}/'

    def save(self, *args, **kwargs):
        if self.tipo == 'socio' or self.tipo == 'socio-moroso':
            self.identificador = self.persona.nombre_apellido

        elif self.tipo == 'nosocio':
            self.identificador = self.noSocio

        elif self.tipo == 'proveedor':
            self.identificador = self.proveedor

        super().save(*args, **kwargs)


class Cobros(models.Model):
    precio = models.FloatField(verbose_name='precio')
    registroEstacionamiento = models.ForeignKey(RegistroEstacionamiento, on_delete=models.CASCADE, verbose_name='registroEstacionamiento')


class CicloCaja(models.Model):
    cicloCaja = models.IntegerField(verbose_name='cicloCaja')


class CicloMensual(models.Model):
    cicloMensual = models.IntegerField(verbose_name='cicloMensual')
