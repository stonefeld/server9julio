from django.db import models
from django.utils.timezone import now, localtime

from usuario.models import Persona

class EntradaGeneral(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    lugar = models.CharField(max_length=30)
    tiempo = models.DateTimeField(default=now)
    direccion = models.CharField(max_length=30, default='ENTRADA')

    def __str__(self):
        return str(localtime(self.tiempo)) + " - " + str(self.persona)

