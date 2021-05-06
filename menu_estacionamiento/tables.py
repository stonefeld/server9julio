import django_tables2 as tables

class HistorialCajas(tables.Table):  # Necesita Tipo de dato
    #cicloMensual__cicloAnual__cicloAnual = tables.Column()
    cicloMensual__cicloMensual = tables.Column(linkify=True)
    cicloCaja = tables.Column()
    recaudado = tables.Column()

    class Meta:
        template_name = 'table_template.html'
        order_by = '-id'
        empty_text = 'No hay ningun ciclo Registrado'