from django.contrib import admin
from .models import (
    RegistroEstacionamiento, Proveedor,
    CicloCaja, CicloMensual, CicloAnual
)

admin.site.register(RegistroEstacionamiento)
admin.site.register(Proveedor)
admin.site.register(CicloCaja)
admin.site.register(CicloMensual)
admin.site.register(CicloAnual)
