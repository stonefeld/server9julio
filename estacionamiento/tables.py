import django_tables2 as tables


class HistorialEstacionamientoTable(tables.Table):  # Necesita Tipo de dato
    identificador = tables.Column(linkify=True)
    tipo = tables.Column()
    tiempo = tables.Column()
    direccion = tables.Column()
    autorizado = tables.Column()
    pago = tables.Column()

    class Meta:
        template_name = 'table_template.html'
        order_by = '-tiempo'
        empty_text = 'No hay ninguna entrada registrada'


class EstacionadosTable(tables.Table):  # Necesita Tipo de dato
    registroEstacionamiento__identificador = tables.Column(linkify=True)
    registroEstacionamiento__tipo = tables.Column()
    registroEstacionamiento__tiempo = tables.Column()
    registroEstacionamiento__direccion = tables.Column()
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
        row_attrs = {
            'id': 'proveedores'
        }
