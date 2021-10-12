import django_tables2 as tables

from estacionamiento.models import CicloCaja


class HistorialCajas(tables.Table):
    cicloMensual = tables.Column(linkify=True, verbose_name='Mes')
    inicioMes = tables.Column(verbose_name='Fecha de inicio del mes')
    finalMes = tables.Column(verbose_name='Fecha de cierre del mes')
    recaudado = tables.Column(verbose_name='Recaudado', empty_values=(), attrs={
        'td': {
            'id': lambda record: f'recaudado-{record.cicloMensual}'
        }
    })
    mas_info = tables.Column(default='Error', verbose_name='Más información', attrs={
        'td': {
            'id': lambda record: record.cicloMensual,
            'class': 'mas-info-btn'
        }
    })

    class Meta:
        template_name = 'table_template.html'
        order_by = '-id'
        empty_text = 'No hay ningun ciclo Registrado'

    def render_recaudado(self, record):
        ciclos_caja = CicloCaja.objects.all().filter(cicloMensual__cicloMensual=record.cicloMensual)
        total_recaudado = 0
        for ciclo in list(ciclos_caja.values()):
            if ciclo['recaudado'] is not None:
                total_recaudado += ciclo['recaudado']

        return f'${total_recaudado}'
