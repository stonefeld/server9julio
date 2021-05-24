from django.contrib import admin
from .models import (
    RegistroEstacionamiento, Proveedor,
    CicloCaja, CicloMensual, CicloAnual,
    TarifaEspecial, Dia_Especial,
    Horarios_Precio, Cobros
)

admin.site.register(RegistroEstacionamiento)
admin.site.register(Proveedor)
admin.site.register(CicloCaja)
admin.site.register(CicloMensual)
admin.site.register(CicloAnual)
admin.site.register(TarifaEspecial)
admin.site.register(Dia_Especial)
admin.site.register(Horarios_Precio)
admin.site.register(Cobros)
