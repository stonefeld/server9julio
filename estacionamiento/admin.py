from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _

from .models import (
    RegistroEstacionamiento, Proveedor, CicloCaja,
    CicloMensual, CicloAnual, TarifaEspecial, DiaEspecial,
    HorariosPrecio, Cobros, TiempoTolerancia
)


class DeudaFilter(SimpleListFilter):
    title = _('deuda')
    parameter_name = 'deuda'

    def lookups(self, request, model_admin):
        return (
            (None, _('No')),
            ('true', _('Si')),
            ('all', _('Todos/as'))
        )

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup
                }, []),
                'display': title
            }

    def queryset(self, request, queryset):
        if self.value() == 'true':
            return queryset.filter(deuda=True)

        elif self.value() is None:
            return queryset.filter(deuda=False)

        elif self.value() == 'all':
            return queryset


class CobrosAdmin(admin.ModelAdmin):
    list_display = ('usuarioCobro', 'registroEstacionamiento', 'precio')
    list_filter = [DeudaFilter]


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
