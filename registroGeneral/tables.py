import django_tables2 as tables

from .models import EntradaGeneral
from usuario.models import Persona

class EntradaGeneralTable(tables.Table):
    seleccion = tables.CheckBoxColumn(accessor='id')

    class Meta:
        model = Persona
        template_name = 'table_template.html'
        fields = ['nrSocio', 'nombre_apellido', 'nrTarjeta', 'dni', 'general', 'deuda']
        order_by = 'nombre_apellido'
        orderable = True

class EntradaGeneralNoAutorizadaTable(tables.Table):
    class Meta:
        model = Persona
        template_name = 'table_template.html'
        fields = ['nrSocio', 'nombre_apellido', 'nrTarjeta', 'dni', 'deuda']
        order_by = 'nombre_apellido'
        orderable = True
        row_attrs = {
            'name': 'pks',
            'value': lambda record: record.id,
        }

class HistorialTable(tables.Table):
    class Meta:
        model = EntradaGeneral
        template_name = 'table_template.html'
        fields = ['persona', 'lugar', 'tiempo', 'direccion', 'autorizado']
        order_by = '-tiempo'
        orderable = True
        empty_text = 'No hay ninguna entrada registrada'

