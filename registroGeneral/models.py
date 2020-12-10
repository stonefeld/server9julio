from django.db import models
from django.utils.timezone import now, localtime

from usuario.models import Persona

class EntradaGeneral(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, verbose_name='Persona')
    lugar = models.CharField(max_length=30, verbose_name='Lugar')
    tiempo = models.DateTimeField(default=now, verbose_name='Fecha y Hora')
    direccion = models.CharField(max_length=30, default='ENTRADA', verbose_name='Dirección')

    def __str__(self):
        return str(localtime(self.tiempo)) + " - " + str(self.persona)

