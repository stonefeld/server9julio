import django_tables2 as tables


class HistorialEstacionamientoTable(tables.Table):
    identificador = tables.Column(linkify=True, attrs={
        'a': {'class': 'origen'}
    })
    tipo = tables.Column()
    tiempo = tables.Column()
    direccion = tables.Column()
    autorizado = tables.Column()
    pago = tables.Column()

    class Meta:
        template_name = 'table_template.html'
        order_by = '-tiempo'
        empty_text = 'No hay ninguna entrada registrada'


class EstacionadosTable(tables.Table):
    registroEstacionamiento__identificador = tables.Column(linkify=True, attrs={
        'a': {'class': 'origen'}
    })
    registroEstacionamiento__tipo = tables.Column()
    registroEstacionamiento__tiempo = tables.Column()
    registroEstacionamiento__autorizado = tables.Column()
    registroEstacionamiento__pago = tables.Column()

    class Meta:
        template_name = 'table_template.html'
        order_by = '-registroEstacionamiento__tiempo'
        empty_text = 'No hay ninguna entrada registrada'


class ProveedoresTable(tables.Table):
    idProveedor = tables.Column()
    nombre_proveedor = tables.Column()

    class Meta:
        template_name = 'table_template.html'
        order_by = '-tiempo'
        empty_text = 'No hay ninguna entrada registrada'
        row_attrs = {'id': 'proveedores'}
