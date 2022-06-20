from django.db import models


class Persona(models.Model):
    nombre_apellido = models.CharField(max_length=120, verbose_name='Nombre y apellido')
    dni = models.IntegerField(null=True, verbose_name='DNI')
    nrTarjeta = models.IntegerField(null=True, blank=True, verbose_name='Nr. de tarjeta')
    nrSocio = models.IntegerField(null=True, blank=True, verbose_name='Nr. de socio')
    general = models.BooleanField(default=False, verbose_name='Autorización para entrar')
    estacionamiento = models.BooleanField(default=False, verbose_name='Autorización para estacionamiento')
    tenis = models.BooleanField(default=False, verbose_name='Autorización para tenis')
    deuda = models.FloatField(null=True, verbose_name='Deuda', default=0)

    def __str__(self):
        return str(self.nombre_apellido)

    def get_absolute_url(self):
        return f'/usuario/lista/{self.id}/'

    def save(self, no_existe=False, *args, **kwargs):
        if not no_existe:
            deuda_max = Deuda.objects.last()
            if self.deuda < deuda_max.deuda:
                self.general = True

            else:
                self.general = False

            if self.deuda < deuda_max.deudaEstacionamiento:
                self.estacionamiento = True

            else:
                self.estacionamiento = False

        super().save(*args, **kwargs)


class Deuda(models.Model):
    deuda = models.FloatField(default=300, verbose_name='Deuda general como socio')
    deudaEstacionamiento = models.FloatField(default=300, verbose_name='Deuda máxima del estacionamiento')

    class Meta:
        verbose_name = 'Deuda'
        verbose_name_plural = 'Deudas'

    def __str__(self):
        return f'Deuda socio de ${self.deuda} y para estacionamiento de ${self.deudaEstacionamiento}'
