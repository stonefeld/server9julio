from django.contrib import admin
from .models import (
    RegistroEstacionamiento, Proveedor, CicloCaja,
    CicloMensual, CicloAnual, TarifaEspecial, DiaEspecial,
    HorariosPrecio, Cobros, TiempoTolerancia
)


class CobrosAdmin(admin.ModelAdmin):
    list_display = ('usuarioCobro', 'registroEstacionamiento', 'precio')


admin.site.register(RegistroEstacionamiento)
admin.site.register(Proveedor)
admin.site.register(CicloCaja)
admin.site.register(CicloMensual)
admin.site.register(CicloAnual)
admin.site.register(TarifaEspecial)
admin.site.register(DiaEspecial)
admin.site.register(HorariosPrecio)
admin.site.register(Cobros, CobrosAdmin)
admin.site.register(TiempoTolerancia)
