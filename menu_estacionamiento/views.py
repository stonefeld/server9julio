from datetime import date

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from django_tables2 import RequestConfig

from estacionamiento.models import (
    RegistroEstacionamiento, Proveedor,
    CicloCaja, CicloMensual, Persona, CicloAnual, Cobros, Estacionado
)
from estacionamiento.forms import ProveedorForm
from estacionamiento.tables import EstacionadosTable, ProveedoresTable


@login_required
def menu_estacionamiento(request):
    return render(
        request,
        template_name='menu_estacionamiento/inicio_estacionamiento.html',
        context={}
    )


@login_required
def seleccionarCalendario(request):
    return render(
        request,
        template_name='menu_estacionamiento/calendario.html',
        context={}
    )


@login_required
def resumenTiempoReal(request):
    if request.method == 'GET':
        estacionamiento = Estacionado.objects.all()
        busqueda = request.GET.get('buscar')
        fecha = request.GET.get('fecha')
        tiempo = request.GET.get('tiempo')

        if busqueda:
            estacionamiento = estacionamiento.filter(
                Q(registroEstacionamiento__identificador__icontains=busqueda),
            ).distinct()

        if fecha:
            fecha = str(fecha).split('-')
            fecha = date(int(fecha[0]), int(fecha[1]), int(fecha[2]))
            estacionamiento = estacionamiento.filter(
                registroEstacionamiento__tiempo__date=fecha
            )

        if tiempo:
            tiempo = str(tiempo).split(':')
            tiempo = time(int(tiempo[0]), int(tiempo[1]))
            estacionamiento = estacionamiento.filter(
                registroEstacionamiento__tiempo__hour=tiempo.hour,
                registroEstacionamiento__tiempo__minute=tiempo.minute
            )

        table = EstacionadosTable(estacionamiento)
        RequestConfig(request).configure(table)

        return render(
            request,
            'menu_estacionamiento/resumen_tiempo.html',
            {'table': table, 'title': 'Historial'}
        )

    return render(
        request,
        template_name='menu_estacionamiento/resumen_tiempo.html',
        context={}
    )


@login_required
def proveedores(request):
    proveedores = Proveedor.objects.all()
    table = ProveedoresTable(proveedores)
    RequestConfig(request).configure(table)

    context = {
        'table': table,
        'title': 'Lista de proveedores'
    }

    return render(
        request,
        template_name='menu_estacionamiento/proveedores.html',
        context=context
    )


@login_required
def historial(request):
    return render(
        request,
        template_name='menu_estacionamiento/historial.html',
        context={}
    )
