from datetime import date
import json
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django_tables2 import RequestConfig

from estacionamiento.models import (
    RegistroEstacionamiento, Proveedor,
    CicloCaja, CicloMensual, Persona, CicloAnual, Cobros, Estacionado, Horarios_Precio, TarifaEspecial
)
from estacionamiento.forms import ProveedorForm
from estacionamiento.tables import EstacionadosTable, ProveedoresTable
from .tables import HistorialCajas
from django.views.decorators.csrf import csrf_exempt


@login_required
def menu_estacionamiento(request):
    return render(
        request,
        template_name='menu_estacionamiento/inicio_estacionamiento.html',
        context={}
    )

@csrf_exempt
@login_required
def seleccionarCalendario(request):
    if request.method == 'POST':
        r = request.body
        data = json.loads(r.decode())
        i = 0
        for tarifa in data:
            i = i + 1
            horario = Horarios_Precio.objects.get(id = i)
            horario.inicio = tarifa['Inicio']
            horario.final = tarifa['Final']
            horario.precio = float(tarifa['tarifa'].replace(',','.'))
            horario.save()
        return JsonResponse('Ok', safe=False)
    else:
        horariosPrecios = Horarios_Precio.objects.all()
        tarifaEspecial = TarifaEspecial.objects.all().last().precio
        return render(
            request,
            template_name='menu_estacionamiento/calendario.html',
            context={"horariosPrecios" : horariosPrecios,
                    "tarifaEspecial" : tarifaEspecial}
            )

@csrf_exempt
def tarifasEspeciales(request):
    r = request.body
    data = json.loads(r.decode())
    print(data)
    TarifaEspecial(precio=data.replace(',','.')).save()
    return JsonResponse('Ok', safe = False)


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

@login_required
def historial_cajas(request):
    cajas = CicloCaja.objects.all()
    table = HistorialCajas(cajas)
    RequestConfig(request).configure(table)

    context = {
        'table': table,
        'title': 'HistorialCajas'
    }
    return render(
        request,
        template_name='menu_estacionamiento/historialCajas.html',
        context = context 
    )
