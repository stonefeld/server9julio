from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _

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


class RegistroEstacionamientoAdmin(admin.ModelAdmin):
    list_display = ('identificador', 'tipo', 'tiempo', 'direccion', 'autorizado', 'pago')
    ordering = ('-tiempo', )


class HorariosPrecioAdmin(admin.ModelAdmin):
    list_display = ('edit_link', 'inicio', 'final', 'precio')
    ordering = ('inicio', )

    def edit_link(self, obj):
        return 'Editar'

    edit_link.short_description = ''


class ProveedorAdmin(admin.ModelAdmin):
    search_fields = ('idProveedor', 'nombre_proveedor')
    list_display = ('idProveedor', 'nombre_proveedor')


class TarifaEspecialAdmin(admin.ModelAdmin):
    list_display = ('edit_link', 'precio')

    def edit_link(self, obj):
        return 'Editar'

    edit_link.short_description = ''


class TiempoToleranciaAdmin(admin.ModelAdmin):
    list_display = ('edit_link', 'tiempo')

    def edit_link(self, obj):
        return 'Editar'

    edit_link.short_description = ''


admin.site.register(RegistroEstacionamiento, RegistroEstacionamientoAdmin)
admin.site.register(Proveedor, ProveedorAdmin)
admin.site.register(CicloCaja)
admin.site.register(CicloMensual)
admin.site.register(CicloAnual)
admin.site.register(TarifaEspecial, TarifaEspecialAdmin)
admin.site.register(DiaEspecial)
admin.site.register(HorariosPrecio, HorariosPrecioAdmin)
admin.site.register(Cobros, CobrosAdmin)
admin.site.register(TiempoTolerancia, TiempoToleranciaAdmin)
