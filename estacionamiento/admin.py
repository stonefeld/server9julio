from django.contrib import admin
from .models import (
    RegistroEstacionamiento, Proveedor,
    CicloCaja, CicloMensual, CicloAnual, Cobros
)

admin.site.register(RegistroEstacionamiento)
admin.site.register(Proveedor)
admin.site.register(CicloCaja)
admin.site.register(CicloMensual)
admin.site.register(CicloAnual)
admin.site.register(Cobros)
