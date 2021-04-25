import django_tables2 as tables

from .models import Persona


class PersonaTable(tables.Table):
    nombre_apellido = tables.Column(accessor='nombre_apellido', linkify=True)

    class Meta:
        model = Persona
        template_name = 'table_template.html'
        fields = ['nrSocio',
                  'nombre_apellido',
                  'nrTarjeta',
                  'dni',
                  'general',
                  'deuda']
        order_by = 'nombre_apellido'
        orderable = True
