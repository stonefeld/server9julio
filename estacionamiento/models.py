from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
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
        verbose_name = 'Apertura Manual'
        verbose_name_plural = 'Aperturas Manuales'


class Proveedor(models.Model):
    idProveedor = models.CharField(max_length=30, verbose_name='ID')
    nombre_proveedor = models.CharField(
            max_length=30, verbose_name='Proveedor')

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'

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
        verbose_name = 'Ciclo Anual'
        verbose_name_plural = 'Ciclos Anuales'

    def __str__(self):
        return f'Año: {self.cicloAnual}'


class CicloMensual(models.Model):
    cicloMensual = models.IntegerField(verbose_name='cicloMensual')
    cicloAnual = models.ForeignKey(CicloAnual, on_delete=models.CASCADE,
                                   verbose_name='cicloAnual')
    inicioMes = models.DateTimeField(verbose_name='inicio',
                                     null=True, blank=True)
    finalMes = models.DateTimeField(verbose_name='final',
                                    null=True, blank=True)

    # Todo debe de hacerse desde el view.
    class Meta:
        verbose_name = 'Ciclo Mensual'
        verbose_name_plural = 'Ciclos Mensuales'

    def __str__(self):
        return f'Mes: {self.cicloMensual} Año: {self.cicloAnual.cicloAnual}'


class CicloCaja(models.Model):
    cicloCaja = models.IntegerField(verbose_name='cicloCaja')
    recaudado = models.IntegerField(
            null=True, blank=True, verbose_name='recaudado')
    cicloMensual = models.ForeignKey(
            CicloMensual, on_delete=models.CASCADE,
            verbose_name='cicloMensual')
    inicioCaja = models.DateTimeField(verbose_name='inicio',
                                      null=True, blank=True)
    finalCaja = models.DateTimeField(verbose_name='final',
                                     null=True, blank=True)
    usuarioCaja = models.ForeignKey(User, on_delete=models.CASCADE,
                                    null=True, blank=True)

    class Meta:
        verbose_name = 'Ciclo Caja'
        verbose_name_plural = 'Ciclos Caja'

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

    AUTORIZADO_CHOICES = (('TRUE', 'TRUE'),
                          ('FALSE', 'FALSE'),
                          ('TIEMPO TOLERANCIA', 'T.T'))

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
    autorizado = models.CharField(
        max_length=30, choices=AUTORIZADO_CHOICES,
        verbose_name='Autorización', default='FALSE')
    cicloCaja = models.ForeignKey(
            CicloCaja, on_delete=models.CASCADE, verbose_name='cicloCaja')
    aperturaManual = models.ForeignKey(
            AperturaManual, on_delete=models.CASCADE,
            verbose_name='AperturaManual', null=True, blank=True)
    usuarioEditor = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    pago = models.CharField(
        max_length=30, verbose_name='pago', null=True, blank=True)

    def __str__(self):
        return f'{self.tiempo} - {self.identificador}'

    def get_absolute_url(self):
        return f'/estacionamiento/historial/{self.id}'

    def save(self, *args, **kwargs):
        if self.tipo == 'SOCIO' or self.tipo == 'SOCIO-MOROSO':
            self.identificador = self.persona.nombre_apellido
            self.noSocio = self.persona.dni

        elif self.tipo == 'NOSOCIO':
            self.identificador = self.noSocio

        elif self.tipo == 'PROVEEDOR':
            self.identificador = self.proveedor.nombre_proveedor

        elif self.tipo == 'MANUAL':
            self.identificador = self.aperturaManual.razon

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Registro Estacionamiento'
        verbose_name_plural = 'Registros Estacionamiento'


class Cobros(models.Model):
    precio = models.FloatField(verbose_name='precio')
    deuda = models.BooleanField(default=False, verbose_name='deuda')
    usuarioCobro = models.ForeignKey(User, on_delete=models.CASCADE,
                                     null=True, blank=True)
    registroEstacionamiento = models.ForeignKey(
            RegistroEstacionamiento, on_delete=models.CASCADE,
            verbose_name='registroEstacionamiento')

    class Meta:
        verbose_name = "Cobro"
        verbose_name_plural = "Cobros"

    def __str__(self):
        return f'Usuario: {self.registroEstacionamiento.identificador} - Precio: ${self.precio}'


class Estacionado(models.Model):
    registroEstacionamiento = models.ForeignKey(
                RegistroEstacionamiento, on_delete=models.CASCADE,
                verbose_name='Registro Estacionamiento')

    def __str__(self):
        return f'{self.registroEstacionamiento.tiempo} - {self.registroEstacionamiento.identificador}'

    def get_absolute_url(self):
        return f'/estacionamiento/historial/{self.registroEstacionamiento.id}/'


class Horarios_Precio(models.Model):
    inicio = models.TimeField(default='00:00:00', verbose_name='Inicio')
    final = models.TimeField(default='00:00:00', verbose_name='Fín')
    precio = models.FloatField(default=250.0, verbose_name='Precio')

    class Meta:
        verbose_name = 'Precio de Horarios'
        verbose_name_plural = 'Precios de Horarios'

    def __str__(self):
        return f'Horario de inicio: {self.inicio}, horario de fin: {self.final}, precio: {self.precio}'


class Dia_Especial(models.Model):
    dia_Especial = models.DateField(verbose_name='Día Especial')

    class Meta:
        verbose_name = 'Día Especial'
        verbose_name_plural = 'Días Especiales'

    def __str__(self):
        return f'Día Especial: {self.dia_Especial}'


class TarifaEspecial(models.Model):
    precio = models.FloatField(default=250.0, verbose_name='Precio')

    class Meta:
        verbose_name = 'Tarifa Especial'
        verbose_name_plural = 'Tarifas Especiales'

    def __str__(self):
        return f'Tarifa especial: {self.precio}'


class TiempoTolerancia(models.Model):
    tiempo = models.IntegerField(verbose_name='tiempo', default=15)

    class Meta:
        verbose_name = 'Tiempo de Tolerancia'
        verbose_name_plural = 'Tiempos de Tolerancia'

    def __str__(self):
        return f'Tiempo de tolerancia: {self.timpo}'
