from estacionamiento.models import Cobros
from django.contrib import admin
from .models import Persona,Deuda

class PersonaAdmin(admin.ModelAdmin):
    search_fields = ('nombre_apellido', 'dni', 'nrTarjeta', 'nrSocio')

admin.site.register(Persona, PersonaAdmin)
admin.site.register(Deuda)

