import csv
from datetime import date, time, timedelta
from threading import Thread
import os

from django.conf import settings
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils.timezone import now

from django_tables2 import RequestConfig

from .models import (
    RegistroEstacionamiento, Proveedor,
    CicloCaja, CicloMensual, Persona, CicloAnual,
    Cobros, Estacionado, AperturaManual
)
from .forms import EstacionamientoForm, AperturaManualForm
from .tables import HistorialEstacionamientoTable


def postpone(function):
    def decorator(*args, **kwargs):
        t = Thread(target=function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()

    return decorator


@postpone
def socket_arduino(cantidad):
    base_dir = settings.BASE_DIR
    script_loc = os.path.join(base_dir, 'scripts/client.py')
    os.system(f'python3 {script_loc} abrir_tiempo {cantidad}')

def apertura_Manual(request):
    form = AperturaManualForm(request.POST or None)
    if form.is_valid():
        form.save()

    if request.method == 'POST':
        return redirect('estacionamiento:historial')

    else:
        return render(request, 'estacionamiento/apertura_manual.html',
                      {'form': form, 'title': 'Apertura Manual'})



@login_required
def apertura_Manual(request):
    form = AperturaManualForm(request.POST or None)
    if form.is_valid():
        form.save()

    if request.method == 'POST':
        return redirect('estacionamiento:historial')

    else:
        return render(request, 'estacionamiento/apertura_manual.html',
                      {'form': form, 'title': 'Apertura Manual'})


@login_required
def pago_deuda(request, id):
    entradaMoroso = RegistroEstacionamiento.objects.get(id=id)
    salida = str(entradaMoroso.persona.deuda) 
    cobroDeuda = Cobros(precio=entradaMoroso.persona.deuda,
                        registroEstacionamiento=entradaMoroso, deuda=True)
    socioMoroso = entradaMoroso.persona
    socioMoroso.deuda = 0.0
    socioMoroso.general = True
    socioMoroso.save()
    cobroDeuda.save()
    entradaMoroso.tipo = 'SOCIO'
    entradaMoroso.autorizado = True
    entradaMoroso.save()
    return HttpResponse(salida)


def emision_resumen_mensual(request):  # Falta testing
    cicloCaja_ = CicloCaja.objects.all().last()
    if cicloCaja_.recaudado is not None:
        cicloMensual_ = CicloMensual.objects.all().last()
        resumen_mensual = RegistroEstacionamiento.objects.\
            values("persona__nombre_apellido", "persona__nrSocio").\
            annotate(cantidad_Entradas=Count("id")).\
            order_by("persona__nombre_apellido").\
            exclude(persona__isnull=True).\
            filter(direccion='SALIDA', cicloCaja__cicloMensual=cicloMensual_, autorizado = True)

        output = []
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        output.append(['NrSocio', 'Persona', 'Cantidad_Entradas'])

        for entrada in resumen_mensual:
            output.append([entrada['persona__nrSocio'],
                           entrada['persona__nombre_apellido'],
                           entrada['cantidad_Entradas']])

        writer.writerows(output)
        response['Content-Disposition'] = \
            'attachment; filename="Resumen_Mensual.csv"'
        cicloAnual_ = CicloAnual.objects.all().last()

        if (cicloMensual_.cicloMensual >= 12):
            cicloAnual_ = CicloAnual(cicloAnual=(cicloAnual_.cicloAnual + 1))
            cicloAnual_.save()
            cicloAnual_ = CicloAnual.objects.all().last()
            cicloMensual_ = CicloMensual(cicloMensual=1,
                                         cicloAnual=cicloAnual_)
            cicloMensual_.save()

        else:
            cicloMensual_ = CicloMensual(
                cicloMensual=(cicloMensual_.cicloMensual + 1),
                cicloAnual=cicloAnual_
            )
            cicloMensual_.save()

        cicloMensual_ = CicloMensual.objects.all().last()
        cicloCaja_ = CicloCaja(cicloCaja=1, cicloMensual=cicloMensual_)
        cicloCaja_.save()
        return response

    else:
        return HttpResponse("Error debe cerrar la caja primero")


@login_required
def cierre_caja(request):  # Cierre de caja con contraseña? / Falta testing
    cicloCaja_ = CicloCaja.objects.all().last()
    recaudado = Cobros.objects.filter(
        registroEstacionamiento__cicloCaja=cicloCaja_, deuda=False).\
        aggregate(recaudacion=Sum('precio'))

    if recaudado['recaudacion']:
        cicloCaja_.recaudado = recaudado['recaudacion']
        cicloCaja_.save()

    else:
        cicloCaja_.recaudado = 0.0
        cicloCaja_.save()
        recaudado['recaudacion'] = '0.0'

    return HttpResponse(recaudado['recaudacion'])


def funcionCobros(dato):
    today = now()
    ayer = today - timedelta(days=1)
    cobro = Cobros.objects.filter(
        Q(registroEstacionamiento__tiempo__range=(ayer, today)) &
        Q(registroEstacionamiento__noSocio__icontains=int(dato)) &
        Q(registroEstacionamiento__Socio__nrTarjeta__icontains=int(dato))
    ).distinct()

    if cobro:
        return False

    else:
        return tiempoTolerancia(dato)

def tiempoTolerancia(dato):
    tolerancia = today - timedelta(minutes=15)
    entrada = RegistroEstacionamiento.objects.filter(
        Q(tiempo__range=(tolerancia, today)),
        Q(noSocio__icontains=int(dato)),
        Q(direccion__icontains='ENTRADA')
    )

    if entrada:
        #no excedio tiempo tolerancia
        return False

    else:
        #excedio tiempo tolerancia
        return True



def funcionEliminarEstacionado(entrada):
    try:
        estacionado = Estacionado.objects.all()
        estacionado.filter(
            registroEstacionamiento__identificador=entrada.identificador
        ).delete()
        return 0

    except:
        return 1


def respuesta(request):
    if request.method == 'GET':
        # El tipo de dato que vamos a recibir (NrTarjeta=0/DNI=1/Proveedor=2)
        tipo = request.GET.get('tipo', '')
        dato = request.GET.get('dato', '')
        direccion_ = request.GET.get('direccion', '')
        cicloCaja_ = CicloCaja.objects.all().last()
        if cicloCaja_.recaudado is not None:
            newCicloCaja = CicloCaja(cicloMensual=cicloCaja_.cicloMensual,
                                     cicloCaja=(cicloCaja_.cicloCaja + 1))
            newCicloCaja.save()
            cicloCaja_ = CicloCaja.objects.all().last()

        if int(direccion_) == 1:
            direccion_ = 'SALIDA'
            if int(tipo) == 0:
                try:
                    user = Persona.objects.get(nrTarjeta=int(dato))
                    if user.general:
                        entrada = RegistroEstacionamiento(
                            tipo='SOCIO',
                            lugar='ESTACIONAMIENTO',
                            persona=user,
                            direccion=direccion_,
                            autorizado=tiempoTolerancia(dato),
                            cicloCaja=cicloCaja_
                        )
                        entrada.save()
                        # abrir barrera
                        rta = '#1'
                        funcionEliminarEstacionado(entrada)

                    else:
                        resultado = funcionCobros(dato)
                        if resultado == False:
                            entrada = RegistroEstacionamiento(
                                tipo='SOCIO-MOROSO',
                                lugar='ESTACIONAMIENTO',
                                persona=user,
                                direccion=direccion_,
                                autorizado=False,
                                cicloCaja=cicloCaja_
                            )
                            entrada.save()
                            rta = '#0'  # Registro Socio Moroso Cobro por NoSocio
                            funcionEliminarEstacionado(entrada)
                        else:
                            rta = '#6'  # NoSocio no pago Deuda o no Pago Entrada
                except:
                    rta = '#2'  # El usuario No existe

            elif int(tipo) == 1:
                try:
                    user = Persona.objects.get(dni=int(dato))
                    if user.general:
                        entrada = RegistroEstacionamiento(
                            tipo='SOCIO',
                            lugar='ESTACIONAMIENTO',
                            persona=user,
                            direccion=direccion_,
                            autorizado=tiempoTolerancia(dato),
                            cicloCaja=cicloCaja_
                        )
                        entrada.save()
                        rta = '#1'
                        funcionEliminarEstacionado(entrada)

                    else:
                        resultado = funcionCobros(dato)
                        if resultado == False:
                            entrada = RegistroEstacionamiento(
                                tipo='SOCIO-MOROSO',
                                lugar='ESTACIONAMIENTO',
                                persona=user,
                                direccion=direccion_,
                                autorizado=False,
                                cicloCaja=cicloCaja_
                            )
                            entrada.save()
                            rta = '#0'  # Registro Socio Moroso Cobro por NoSocio
                            funcionEliminarEstacionado(entrada)
                        else:
                            rta = '#6'  # NoSocio no pago Deuda o no Pago Entrada

                except:
                    if tiempoTolerancia(dato) == False:
                        entrada = RegistroEstacionamiento(
                            tipo='NOSOCIO',
                            lugar='ESTACIONAMIENTO',
                            noSocio=dato,
                            direccion=direccion_,
                            autorizado=True,
                            cicloCaja=cicloCaja_
                        )
                        entrada.save()
                        rta = '#1'
                        funcionEliminarEstacionado(entrada)
                    else:
                        rta = '#5'
                        # El No Socio no pagó y excedió
                        # el tiempo de tolerancia

            else:
                try:
                    proveedor_ = Proveedor.objects.get(idProveedor=int(dato))
                    entrada = RegistroEstacionamiento(
                        tipo='PROVEEDOR',
                        lugar='ESTACIONAMIENTO',
                        proveedor=proveedor_,
                        direccion=direccion_,
                        autorizado=True,
                        cicloCaja=cicloCaja_
                    )
                    entrada.save()
                    # Abrir barrera
                    rta = '#1'
                    funcionEliminarEstacionado(entrada)

                except:
                    rta = '#4'  # Error Proveedor no encontrado

        else:
            direccion_ = 'ENTRADA'
            if int(tipo) == 0:
                try:
                    user = Persona.objects.get(nrTarjeta=int(dato))
                    if user.general:
                        entrada = RegistroEstacionamiento(
                            tipo='SOCIO',
                            lugar='ESTACIONAMIENTO',
                            persona=user,
                            direccion=direccion_,
                            autorizado=True,
                            cicloCaja=cicloCaja_
                        )
                        entrada.save()
                        # Abrir barrera
                        rta = '#1'

                    else:
                        entrada = RegistroEstacionamiento(
                            tipo='SOCIO-MOROSO',
                            lugar='ESTACIONAMIENTO',
                            persona=user,
                            direccion=direccion_,
                            autorizado=False,
                            cicloCaja=cicloCaja_
                        )
                        entrada.save()
                        rta = '#0'  # Registro Socio Moroso

                except:
                    rta = '#2'  # El usuario No existe

            elif int(tipo) == 1:
                try:
                    user = Persona.objects.get(dni=int(dato))
                    if user.general:
                        entrada = RegistroEstacionamiento(
                            tipo='SOCIO',
                            lugar='ESTACIONAMIENTO',
                            persona=user,
                            direccion=direccion_,
                            autorizado=True,
                            cicloCaja=cicloCaja_
                        )
                        entrada.save()
                        rta = '#1'

                    else:
                        entrada = RegistroEstacionamiento(
                            tipo='SOCIO-MOROSO',
                            lugar='ESTACIONAMIENTO',
                            persona=user,
                            direccion=direccion_,
                            autorizado=False,
                            cicloCaja=cicloCaja_
                        )
                        entrada.save()
                        # Abrir barrera
                        rta = '#0'  # Registro Socio Moroso

                except:
                    entrada = RegistroEstacionamiento(
                        tipo='NOSOCIO',
                        lugar='ESTACIONAMIENTO',
                        noSocio=int(dato),
                        direccion=direccion_,
                        autorizado=True,
                        cicloCaja=cicloCaja_
                    )
                    entrada.save()
                    rta = '#3'  # NoSocio registrado

            else:
                try:
                    proveedor_ = Proveedor.objects.get(idProveedor=int(dato))
                    entrada = RegistroEstacionamiento(
                        tipo='PROVEEDOR',
                        lugar='ESTACIONAMIENTO',
                        proveedor=proveedor_,
                        direccion=direccion_,
                        autorizado=True,
                        cicloCaja=cicloCaja_
                    )
                    entrada.save()
                    # Abrir barrera
                    rta = '#1'

                except:
                    rta = '#4'  # Error Proveedor no encontrado
            funcionEliminarEstacionado(entrada)
            estacionado = Estacionado(registroEstacionamiento=entrada)
            estacionado.save()

        return HttpResponse(rta)


@login_required
def historial_estacionamiento(request):
    if request.method == 'GET':
        estacionamiento = RegistroEstacionamiento.objects.all()
        busqueda = request.GET.get('buscar')
        fecha = request.GET.get('fecha')
        tiempo = request.GET.get('tiempo')

        if busqueda:
            estacionamiento = estacionamiento.filter(
                Q(identificador__icontains=busqueda),
            ).distinct()

        if fecha:
            fecha = str(fecha).split('-')
            fecha = date(int(fecha[0]), int(fecha[1]), int(fecha[2]))
            estacionamiento = estacionamiento.filter(
                tiempo__date=fecha
            )

        if tiempo:
            tiempo = str(tiempo).split(':')
            tiempo = time(int(tiempo[0]), int(tiempo[1]))
            estacionamiento = estacionamiento.filter(
                tiempo__hour=tiempo.hour,
                tiempo__minute=tiempo.minute
            )

        table = HistorialEstacionamientoTable(estacionamiento)
        RequestConfig(request).configure(table)

        return render(
            request,
            'estacionamiento/historial.html',
            {'table': table, 'title': 'Historial'}
        )


@login_required
def detalle_estacionamiento(request, id):
    datos = RegistroEstacionamiento.objects.get(id=id)
    return render(request, 'estacionamiento/detalle_historial.html',
                  {'datos': datos, 'title': 'Detalle Historial'})


@login_required
def editar_estacionamiento(request, id):
    obj = RegistroEstacionamiento.objects.get(id=id)
    form = EstacionamientoForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()

    context = {
        'form': form,
        'id': obj.id,
        'title': 'Detalle historial'
    }

    if request.method == 'POST':
        return redirect('estacionamiento:historial')

    else:
        return render(request,
                      'estacionamiento/editar_historial.html',
                      context)


# La unica funcion de este view es la de que el codigo de js pueda hacer un
# a estos datos para renderizarlos en tiempo real sin tener que hacer otro
# request.
def fetch_proveedores(request):
    # Dentro del GET recibe como datos:
    page = request.GET.get('page')  # La pagina que quiere visualizar.
    filter_string = request.GET.get('filter-string')  # El string de filtro.

    # Filtra todos los proveedores con el string recibido por nombre de
    # proveedor.
    proveedores = Proveedor.objects.all().filter(
        Q(nombre_proveedor__icontains=filter_string)
    ).order_by('nombre_proveedor')

    # Realiza la paginacion de los datos con un maximo de 20 proveedores por
    # pagina y especifica la pagina que quiere visualizar.
    paginated = Paginator(list(proveedores.values()), 20)
    proveedores = paginated.page(page).object_list

    # Agrega al json de respuesta los datos para que el codigo de js sepa
    # si la pagina que esta visualizandose tiene pagina siguiente o anterior.
    proveedores.append({
        'has_previous': paginated.page(page).has_previous(),
        'has_next': paginated.page(page).has_next()
    })

    # Devuelve la respuesta en forma de json especificando el 'safe=False'
    # para evitar tener problemas de CORS.
    return JsonResponse(proveedores, safe=False)
