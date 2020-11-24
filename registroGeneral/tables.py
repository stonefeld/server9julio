import django_tables2 as tables

from .models import EntradaGeneral, Persona

class EntradaGeneralTable(tables.Table):
    seleccion = tables.CheckBoxColumn(accessor='id')

    class Meta:
        model = Persona
        template_name = 'table_template.html'
        fields = ['nrSocio', 'nombre_apellido', 'nrTarjeta', 'dni']
        order_by = 'nrSocio'
        orderable = True

