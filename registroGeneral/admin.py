from django.contrib import admin
from .models import EntradaGeneral


class EntradaGeneralAdmin(admin.ModelAdmin):
    search_fields = ('persona__nombre_apellido', 'persona__dni', 'persona__nrSocio', 'persona__nrTarjeta')
    list_display = ('persona', 'lugar', 'tiempo', 'direccion', 'autorizado')
    ordering = ('-tiempo', )


admin.site.register(EntradaGeneral, EntradaGeneralAdmin)
