from datetime import date, time
import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from django_tables2 import RequestConfig

from estacionamiento.models import CicloCaja, CicloMensual, Estacionado, HorariosPrecio, TarifaEspecial
from .tables import HistorialCajas
from estacionamiento.tables import EstacionadosTable


@login_required
def menu_estacionamiento(request):
    return render(
        request,
        template_name='menu_estacionamiento/inicio_estacionamiento.html',
        context={}
    )


@csrf_exempt
@login_required
def seleccionar_calendario(request):
    if request.method == 'POST':
        r = request.body
        data = json.loads(r.decode())
        i = 0
        for tarifa in data:
            i = i + 1
            horario = HorariosPrecio.objects.get(id=i)
            horario.inicio = tarifa['Inicio']
            horario.final = tarifa['Final']
            horario.precio = float(tarifa['tarifa'].replace(',', '.'))
            horario.save()
        messages.warning(request, 'Tarifa Normal Cambiada')
        return JsonResponse('Ok', safe=False)

    else:
        horariosPrecios = HorariosPrecio.objects.all()
        tarifaEspecial = TarifaEspecial.objects.all().last().precio
        context = {'horariosPrecios': horariosPrecios, 'tarifaEspecial': tarifaEspecial}
        return render(request, 'menu_estacionamiento/calendario.html', context)


@csrf_exempt
def tarifas_especiales(request):
    r = request.body
    data = json.loads(r.decode())
    TarifaEspecial(precio=data.replace(',', '.')).save()
    messages.warning(request, 'Tarifa Especial Cambiada')
    return JsonResponse('Ok', safe=False)


@login_required
def playground(request):
    return render(request, 'menu_estacionamiento/playground.html', {'title': 'Playground'})


@login_required
def resumen_tiempo_real(request):
    if request.method == 'GET':
        estacionamiento = Estacionado.objects.all()
        busqueda = request.GET.get('buscar')
        fecha = request.GET.get('fecha')
        tiempo = request.GET.get('tiempo')

        if busqueda:
            estacionamiento = estacionamiento.filter(Q(registroEstacionamiento__identificador__icontains=busqueda)).distinct()

        if fecha:
            fecha = str(fecha).split('-')
            fecha = date(int(fecha[0]), int(fecha[1]), int(fecha[2]))
            estacionamiento = estacionamiento.filter(registroEstacionamiento__tiempo__date=fecha)

        if tiempo:
            tiempo = str(tiempo).split(':')
            tiempo = time(int(tiempo[0]), int(tiempo[1]))
            estacionamiento = estacionamiento.filter(
                registroEstacionamiento__tiempo__hour=tiempo.hour,
                registroEstacionamiento__tiempo__minute=tiempo.minute
            )

        table = EstacionadosTable(estacionamiento)
        RequestConfig(request).configure(table)

        return render(request, 'menu_estacionamiento/resumen_tiempo.html', {'table': table, 'title': 'Resumen en tiempo real'})

    return render(request, 'menu_estacionamiento/resumen_tiempo.html', {})


@login_required
def proveedores(request):
    return render(request, 'menu_estacionamiento/proveedores.html', {'title': 'Lista de proveedores'})


@login_required
def lista_usuarios(request):
    return render(request, 'menu_estacionamiento/lista_usuarios.html', {'title': 'Lista de socios'})


@login_required
def historial(request):
    return render(request, 'menu_estacionamiento/historial.html', {})


@login_required
def historial_cajas(request):
    ciclos_mensual = CicloMensual.objects.all()
    table = HistorialCajas(ciclos_mensual)
    RequestConfig(request).configure(table)
    return render(request, 'menu_estacionamiento/historialCajas.html', {'table': table, 'title': 'Historial Cajas'})


def fetch_ciclo_caja(request):
    ciclo_mensual = request.GET.get('mes')
    order = request.GET.get('order-by')
    ciclos_caja = []

    for ciclo in list(CicloCaja.objects.all().filter(cicloMensual__cicloMensual=ciclo_mensual).values().order_by(order)):
        if ciclo['usuarioCaja_id'] is not None:
            ciclo['user'] = User.objects.get(id=ciclo['usuarioCaja_id']).username

        else:
            ciclo['user'] = None

        ciclos_caja.append(ciclo)

    return JsonResponse(ciclos_caja, safe=False)
