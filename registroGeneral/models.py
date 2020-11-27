from django.db import models
from django.utils import timezone, dateformat

from usuario.models import Persona

class EntradaGeneral(models.Model):
    lugar = models.CharField(max_length=30)
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    tiempo = models.DateTimeField(default=dateformat.format(timezone.now(), 'Y-m-d H:i:s'))
    direccion = models.CharField(max_length=30,default='ENTRADA')

    def __str__(self):
        tiempo = self.tiempo
        return str(tiempo) + " - " + str(self.persona)

