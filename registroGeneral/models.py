from django.db import models
from django.utils import timezone
from usuario.models import Persona

class EntradaGeneral(models.Model):
    lugar = models.CharField(max_length=30)
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    tiempo = models.DateTimeField(default=timezone.now)

