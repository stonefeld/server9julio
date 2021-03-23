import django_tables2 as tables


class HistorialEstacionamientoTable(tables.Table):
    identificador = tables.Column(linkify=True)
    tiempo = tables.Column()
    direccion = tables.Column()
    autorizado = tables.BooleanColumn()

    class Meta:
        template_name = 'table_template.html'
        order_by = '-tiempo'
        empty_text = 'No hay ninguna entrada registrada'
