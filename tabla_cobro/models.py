from django.db import models
from django.utils.timezone import now, localtime

from usuario.models import Persona

class Dia_Especial(models.Model):
    dia = models.IntegerField()
    mes = models.IntegerField()
    año = models.IntegerField()
    precio = models.IntegerField()

class Horarios_Precio(models.Model):
    inicio = models.IntegerField()
    final = models.IntegerField()
    precio = models.IntegerField()
