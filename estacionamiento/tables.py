import django_tables2 as tables


class HistorialEstacionamientoTable(tables.Table): #Necesita Tipo de dato
    identificador = tables.Column(linkify=True)
    tiempo = tables.Column()
    direccion = tables.Column()
    autorizado = tables.BooleanColumn()

    class Meta:
        template_name = 'table_template.html'
        order_by = '-tiempo'
        empty_text = 'No hay ninguna entrada registrada'

class EstacionadosTable(tables.Table): #Necesita Tipo de dato
    registroEstacionamiento__identificador = tables.Column(linkify=True)
    registroEstacionamiento__tiempo = tables.Column()
    registroEstacionamiento__direccion = tables.Column()
    registroEstacionamiento__autorizado = tables.BooleanColumn()

    class Meta:
        template_name = 'table_template.html'
        order_by = '-registroEstacionamiento__tiempo'
        empty_text = 'No hay ninguna entrada registrada'

class Proveedores(tables.Table): #falta hacer
    idProveedor = tables.Column()
    nombre_proveedor = tables.Column()
    
    class Meta:
        template_name = 'table_template.html'
        order_by = '-tiempo'
        empty_text = 'No hay ninguna entrada registrada'
