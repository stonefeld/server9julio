from django.db import models
from django.utils import timezone

class Persona(models.Model):
    nombre = models.CharField(max_length=50)
    dni = models.IntegerField(null=True)
    nrSocio = models.IntegerField(null=True, blank=True)
    nrTarjeta = models.IntegerField(null=True, blank=True)
    general = models.BooleanField(default=False)
    pileta = models.BooleanField(default=False)
    tenis = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % (self.nombre)

class Entrada(models.Model):
    lugar = models.CharField(max_length=30)
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    tiempo = models.DateTimeField(default=timezone.now)

