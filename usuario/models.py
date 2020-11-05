from django.db import models

class Persona(models.Model):
    nombre = models.CharField(max_length=30)
    apellido = models.CharField(max_length=30)
    dni = models.IntegerField()
    nrSocio = models.IntegerField(null=True, blank=True)
    general = models.BooleanField(default=False)
    pileta = models.BooleanField(default=False)
    tenis = models.BooleanField(default=False)

class Entrada(models.Model):
    lugar = models.CharField(max_length=30)
    tiempo = models.DateTimeField(auto_now_add=True)
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)

