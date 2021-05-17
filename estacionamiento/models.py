from datetime import datetime
from django.db import models
from django.utils.timezone import now

from usuario.models import Persona


class AperturaManual(models.Model):
    RAZON_CHOICES = (('FALTA REGISTRO ENTRADA', 'FALTA REGISTRO ENTRADA'),
                     ('CONFLICTO', 'CONFLICTO'))
    DIRECCION_CHOICES = (('ENTRADA', 'ENTRADA'),
                         ('SALIDA', 'SALIDA'))

    razon = models.CharField(max_length=30,
                             verbose_name='razon',
                             choices=RAZON_CHOICES)
    comentario = models.CharField(max_length=300,
                                  verbose_name='comentario',
                                  null=True, blank=True)
    direccion = models.CharField(max_length=30, choices=DIRECCION_CHOICES,
                                 verbose_name='Dirección', default='ENTRADA')

    def __str__(self):
        return str(self.razon)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        entrada = RegistroEstacionamiento(
            tipo='MANUAL',
            lugar='ESTACIONAMIENTO',
            direccion=self.direccion,
            autorizado=False,
            cicloCaja=CicloCaja.objects.all().last(),
            aperturaManual=self
        )
        entrada.save()

    class Meta:
        verbose_name = "AperturaManual"
        verbose_name_plural = "AperturasManuales"


class Proveedor(models.Model):
    idProveedor = models.CharField(max_length=30, verbose_name='ID')
    nombre_proveedor = models.CharField(
            max_length=30, verbose_name='Proveedor')

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"

    def __str__(self):
        return str(self.nombre_proveedor)

    def as_dict(self):
        return {
            'pk': self.id,
            'idProveedor': self.idProveedor,
            'nombre_proveedor': self.nombre_proveedor
        }

    def get_absolute_url(self):
        return f'/estacionamiento/proveedor/{self.id}'


class CicloAnual(models.Model):
    cicloAnual = models.IntegerField(verbose_name='cicloAnual')

    class Meta:
        verbose_name = "Ciclo Anual"
        verbose_name_plural = "Ciclos Anuales"


class CicloMensual(models.Model):
    cicloMensual = models.IntegerField(verbose_name='cicloMensual')
    cicloAnual = models.ForeignKey(
            CicloAnual, on_delete=models.CASCADE, verbose_name='cicloAnual')

    class Meta:
        verbose_name = "Ciclo Mensual"
        verbose_name_plural = "Ciclos Mensuales"
    
    


class CicloCaja(models.Model):
    cicloCaja = models.IntegerField(verbose_name='cicloCaja')
    recaudado = models.IntegerField(
            null=True, blank=True, verbose_name='recaudado')
    cicloMensual = models.ForeignKey(
            CicloMensual, on_delete=models.CASCADE,
            verbose_name='cicloMensual')

    class Meta:
        verbose_name = "Ciclo Caja"
        verbose_name_plural = "Ciclos Caja"

    def __str__(self):
        return f'Caja: {self.cicloCaja} Mes: {self.cicloMensual.cicloMensual} Año: {self.cicloMensual.cicloAnual.cicloAnual}'
    
    def get_absolute_url(self):
        return f'/estacionamiento/emision_resumen/{self.id}'


class RegistroEstacionamiento(models.Model):
    TIPO_CHOICES = (('SOCIO', 'SOCIO'),
                    ('SOCIO-MOROSO', 'SOCIO-MOROSO'),
                    ('NOSOCIO', 'NOSOCIO'),
                    ('PROVEEDOR', 'PROVEEDOR'),
                    ('MANUAL', 'MANUAL'))

    DIRECCION_CHOICES = (('ENTRADA', 'ENTRADA'),
                         ('SALIDA', 'SALIDA'))

    tipo = models.CharField(
            max_length=30, verbose_name='Tipo',
            choices=TIPO_CHOICES, default='SOCIO')
    identificador = models.CharField(
            max_length=30, verbose_name='Identificador',
            null=True, blank=True, default="Error")
    persona = models.ForeignKey(
            Persona, on_delete=models.CASCADE,
            verbose_name='Persona', null=True, blank=True)
    noSocio = models.IntegerField(
            verbose_name='DNI', null=True, blank=True)
    proveedor = models.ForeignKey(
            Proveedor, on_delete=models.CASCADE,
            verbose_name='Proveedor', null=True, blank=True)
    lugar = models.CharField(
            max_length=30, verbose_name='Lugar')
    tiempo = models.DateTimeField(
            verbose_name='Fecha y Hora', default=now)
    direccion = models.CharField(
            max_length=30, choices=DIRECCION_CHOICES,
            verbose_name='Dirección', default='ENTRADA')
    autorizado = models.BooleanField(
            verbose_name='Autorización', default=False)
    cicloCaja = models.ForeignKey(
            CicloCaja, on_delete=models.CASCADE, verbose_name='cicloCaja')
    aperturaManual = models.ForeignKey(
            AperturaManual, on_delete=models.CASCADE,
            verbose_name='AperturaManual', null=True, blank=True)

    def __str__(self):
        return f'{self.tiempo} - {self.identificador}'

    def get_absolute_url(self):
        return f'/estacionamiento/historial/{self.id}'

    def save(self, *args, **kwargs):
        if self.tipo == 'SOCIO' or self.tipo == 'SOCIO-MOROSO':
            self.identificador = self.persona.nombre_apellido

        elif self.tipo == 'NOSOCIO':
            self.identificador = self.noSocio

        elif self.tipo == 'PROVEEDOR':
            self.identificador = self.proveedor.nombre_proveedor

        elif self.tipo == 'MANUAL':
            self.identificador = self.aperturaManual.razon

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Registro Estacionamiento"
        verbose_name_plural = "Registros Estacionamiento"


class Cobros(models.Model):
    precio = models.FloatField(verbose_name='precio')
    deuda = models.BooleanField(default=False, verbose_name='deuda')
    registroEstacionamiento = models.ForeignKey(
            RegistroEstacionamiento, on_delete=models.CASCADE,
            verbose_name='registroEstacionamiento')


class Estacionado(models.Model):
    registroEstacionamiento = models.ForeignKey(
                RegistroEstacionamiento, on_delete=models.CASCADE,
                verbose_name='registroEstacionamiento')

    def __str__(self):
        return f'{self.tiempo} - {self.identificador}'

    def get_absolute_url(self):
        return f'/estacionamiento/historial/{self.registroEstacionamiento.id}/'


class Dia_Especial(models.Model):
    dia_Especial = models.DateField(verbose_name="DiaEspecial")

class Horarios_Precio(models.Model):
    inicio = models.TimeField(default="00:00:00")
    final = models.TimeField(default="00:00:00")
    precio = models.FloatField(default=250.0)

class TarifaEspecial(models.Model):
    precio = models.FloatField(default=250.0)
