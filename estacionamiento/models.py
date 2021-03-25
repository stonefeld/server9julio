from django.db import models
from django.utils.timezone import now, localtime

from usuario.models import Persona

class Proveedor(models.Model):
    idProveedor = models.CharField(max_length=30, verbose_name='idProveedor')
    nombre_proveedor = models.CharField(max_length=30, verbose_name='Proveedor')
    def __str__(self):
        return str(self.nombre_proveedor)

    def __str__(self):
        return str(self.nombre_proveedor)

class CicloAnual(models.Model):
    cicloAnual = models.IntegerField(verbose_name='cicloAnual')

class CicloMensual(models.Model):
    cicloMensual = models.IntegerField(verbose_name='cicloMensual')
    cicloAnual = models.ForeignKey(CicloAnual, on_delete=models.CASCADE, verbose_name='cicloAnual')

class CicloCaja(models.Model):
    cicloCaja = models.IntegerField(verbose_name='cicloCaja')
    recaudado = models.IntegerField(null=True, blank=True ,verbose_name='recaudado')
    cicloMensual = models.ForeignKey(CicloMensual, on_delete=models.CASCADE, verbose_name='cicloMensual')

class RegistroEstacionamiento(models.Model):
    tipo = models.CharField(max_length=30, verbose_name='Tipo')
    identificador = models.CharField(max_length=30, verbose_name='Identificador', null=True, blank=True, default="Error")
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, verbose_name='Persona', null=True, blank=True)
    noSocio = models.IntegerField(verbose_name='DNI', null=True, blank=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, verbose_name='Proveedor', null=True, blank=True)
    lugar = models.CharField(max_length=30, verbose_name='Lugar')
    tiempo = models.TimeField(default=now, verbose_name='Hora')
    fecha = models.DateField(default=now, verbose_name='Fecha')
    direccion = models.CharField(max_length=30, default='ENTRADA', verbose_name='Dirección')
    autorizado = models.BooleanField(default=False, verbose_name='Autorización')
    cicloCaja = models.ForeignKey(CicloCaja, on_delete=models.CASCADE, verbose_name='cicloCaja')
    

    def __str__(self):
        if self.tipo == "SOCIO" or self.tipo == "SOCIO-MOROSO":
            return str(localtime(self.tiempo)) + " - " + str(self.persona)

        elif self.tipo == "NOSOCIO":
            return str(localtime(self.tiempo)) + " - " + str(self.noSocio)

        elif self.tipo == "PROVEEDOR":
            return str(localtime(self.tiempo)) + " - " + str(self.proveedor)

        else:
            return "Error Fatal"
    
    def get_absolute_url(self):
        return f'/estacionamiento/historial/{self.id}/'

    def get_absolute_url(self):
        return f'/estacionamiento/historial/{self.id}/'


class Cobros(models.Model):
    precio = models.FloatField(verbose_name='precio')
    registroEstacionamiento = models.ForeignKey(RegistroEstacionamiento, on_delete=models.CASCADE, verbose_name='registroEstacionamiento')









