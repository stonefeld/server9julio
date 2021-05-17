import django_tables2 as tables


class HistorialCajas(tables.Table):  # Necesita Tipo de dato
    cicloMensual__cicloMensual = tables.Column(linkify=True, verbose_name="Mes")
    cicloMensual__cicloAnual__cicloAnual = tables.Column(verbose_name="Año")
    cicloCaja = tables.Column(verbose_name="Caja")
    recaudado = tables.Column()

    class Meta:
        template_name = 'table_template.html'
        order_by = '-id'
        empty_text = 'No hay ningun ciclo Registrado'
