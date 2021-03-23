import django_tables2 as tables


class HistorialEstacionamientoTable(tables.Table):
    identificador = tables.Column(linkify=True)
    fecha = tables.Column()
    tiempo = tables.Column()
    direccion = tables.Column()
    autorizado = tables.BooleanColumn()

    class Meta:
        template_name = 'table_template.html'
        empty_text = 'No hay ninguna entrada registrada'