from django.contrib import admin
from .models import Persona, Deuda


class PersonaAdmin(admin.ModelAdmin):
    search_fields = ('nombre_apellido', 'dni', 'nrTarjeta', 'nrSocio')
    list_display = ('nombre_apellido', 'dni', 'nrTarjeta', 'nrSocio', 'general', 'estacionamiento', 'deuda')
    ordering = ('nombre_apellido', )


class DeudaAdmin(admin.ModelAdmin):
    list_display = ('edit_link', 'deuda', 'deudaEstacionamiento')

    def edit_link(self, obj):
        return 'Editar'

    edit_link.short_description = ''


admin.site.register(Persona, PersonaAdmin)
admin.site.register(Deuda, DeudaAdmin)
