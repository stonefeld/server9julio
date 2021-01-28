import django_tables2 as tables

from registroGeneral.models import EntradaGeneral

class HistorialTable(tables.Table):
    class Meta:
        model = EntradaGeneral
        template_name = 'table_template.html'
        fields = ['persona', 'lugar', 'tiempo', 'direccion', 'autorizado']
        order_by = '-tiempo'
        orderable = True

