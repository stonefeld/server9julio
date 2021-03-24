from threading import Thread
import os
import csv
from django.utils.timezone import now, localtime
from datetime import datetime, timedelta
from django.db.models import Count
import math
from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse

from django.utils.timezone import localtime

from django.shortcuts import redirect, render

from django_tables2 import RequestConfig

from .models import (
    RegistroEstacionamiento, Proveedor,
    CicloCaja, CicloMensual, Persona
)
from .forms import EstacionamientoForm
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

def emision_resumen_mensual(request):
    cicloMensual = CicloMensual.objects.all().last().cicloMensual
    resumen_mensual = RegistroEstacionamiento.objects.values("persona__nombre_apellido").annotate(cantidad_Entradas = Count("id")).order_by("persona__nombre_apellido").exclude(persona__isnull=True).filter(direccion='ENTRADA', cicloMensual=cicloMensual)
    output=[]
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    output.append(['Persona','Cantidad_Entradas'])
    for entrada in resumen_mensual:
        output.append([entrada['persona__nombre_apellido'], entrada['cantidad_Entradas']])
    writer.writerows(output)
    print(output)
    response['Content-Disposition'] = 'attachment; filename="Resumen_Mensual.csv"'

    return response


def respuesta(request):
    if request.method == 'GET':
        tipo = request.GET.get('tipo', '')  # el tipo de dato que vamos a recibir (NrTarjeta=0/DNI=1/Proveedor=2)
        dato = request.GET.get('dato', '')  # el dato
        direccion_ = request.GET.get('direccion', '')
        cicloCaja_ = CicloCaja.objects.all().last().cicloCaja
        cicloMensual_ = CicloMensual.objects.all().last().cicloMensual

        if int(direccion_) == 1:
            direccion_ = 'SALIDA'
            if int(tipo) == 0:
                try:
                    user = Persona.objects.get(nrTarjeta=int(dato))
                    if user.general == True:
                        entrada = RegistroEstacionamiento(tipo='SOCIO',
                        lugar='ESTACIONAMIENTO',
                        persona=user,
                        direccion=direccion_,
                        autorizado=True,
                        cicloCaja=cicloCaja_,
                        cicloMensual=cicloMensual_,
                        identificador = user.nombre_apellido)
                        entrada.save()
                        #abrir barrera
                        rta = '#1'
                    else:
                        entrada = RegistroEstacionamiento(tipo='SOCIO-MOROSO',
                        lugar='ESTACIONAMIENTO',
                        persona=user,
                        direccion=direccion_,
                        autorizado=False,
                        cicloCaja=cicloCaja_,
                        cicloMensual=cicloMensual_,
                        identificador = user.nombre_apellido)
                        entrada.save()
                        rta = '#0' #Registro Socio Moroso
                except:
                    rta = '#2' #el usuario No existe
            elif int(dato) == 1:
                try:
                    user = Persona.objects.get(dni = int(dato))
                    if user.general == True:
                        entrada = RegistroEstacionamiento(tipo='SOCIO',
                        lugar='ESTACIONAMIENTO',
                        persona=user,
                        direccion=direccion_,
                        autorizado=True,
                        cicloCaja=cicloCaja_,
                        cicloMensual=cicloMensual_,
                        identificador = user.nombre_apellido)
                        entrada.save()
                        rta = '#1'
                    else:
                        entrada = RegistroEstacionamiento(tipo='SOCIO-MOROSO',
                        lugar='ESTACIONAMIENTO',
                        persona=user,
                        direccion=direccion_,
                        autorizado=False,
                        cicloCaja=cicloCaja_,
                        cicloMensual=cicloMensual_,
                        identificador = user.nombre_apellido)
                        entrada.save()
                        #abrir barrera
                        rta = '#0' #Registro Socio Moroso
                except:
                    ayer = now - timedelta(days=1)
                    cobro = Cobros.objects.filter(
                        Q(registroEstacionamiento__tiempo__range = (ayer, now))
                        & Q(registroEstacionamiento__noSocio__icontains = int(dato))
                        ).distinct()
                    if is_empty(cobro) :
                        tolerancia = now - timedelta(minutes=15)
                        entrada = RegistroEstacionamiento.objects.filter(
                            Q(tiempo__range = (tolerancia, now))
                        )
                        if not entrada:
                            rta = '#5' #el No Socio no pagó y excedió el tiempo de tolerancia
                        else:
                            rta = '#1' #dentro del tiempo de tolerancia
                    else:
                        rta = '#1' 

                        
            else:
                try:
                    proveedor_ = Proveedor.objects.get(idProveedor = int(dato))
                    entrada = RegistroEstacionamiento(tipo='PROVEEDOR',
                    lugar='ESTACIONAMIENTO',
                    proveedor=proveedor_,
                    direccion=direccion_,
                    autorizado=True,
                    cicloCaja=cicloCaja_,
                    cicloMensual=cicloMensual_,
                    identificador = proveedor_.nombre_proveedor)
                    #abrir barrera
                    rta = '#1'
                except:
                    rta = '#4' #Error Proveedor no encontrado
                
        else:
            direccion_ = 'ENTRADA'
            if int(tipo) == 0:
                try:
                    user = Persona.objects.get(nrTarjeta=int(dato))
                    if user.general == True:
                        entrada = RegistroEstacionamiento(tipo='SOCIO',
                        lugar='ESTACIONAMIENTO',
                        persona=user,
                        direccion=direccion_,
                        autorizado=True,
                        cicloCaja=cicloCaja_,
                        cicloMensual=cicloMensual_,
                        identificador = user.nombre_apellido)
                        entrada.save()
                        #abrir barrera
                        rta = '#1'
                    else:
                        entrada = RegistroEstacionamiento(tipo='SOCIO-MOROSO',
                        lugar='ESTACIONAMIENTO',
                        persona=user,
                        direccion=direccion_,
                        autorizado=False,
                        cicloCaja=cicloCaja_,
                        cicloMensual=cicloMensual_,
                        identificador = user.nombre_apellido)
                        entrada.save()
                        rta = '#0' #Registro Socio Moroso

                except:
                    rta = '#2' #el usuario No existe
            elif int(tipo) == 1:
                try:
                    user = Persona.objects.get(dni = int(dato))
                    if user.general == True:
                        entrada = RegistroEstacionamiento(tipo='SOCIO',
                        lugar='ESTACIONAMIENTO',
                        persona=user,
                        direccion=direccion_,
                        autorizado=True,
                        cicloCaja=cicloCaja_,
                        cicloMensual=cicloMensual_,
                        identificador = user.nombre_apellido)
                        entrada.save()
                        rta = '#1'
                    else:
                        entrada = RegistroEstacionamiento(tipo='SOCIO-MOROSO',
                        lugar='ESTACIONAMIENTO',
                        persona=user,
                        direccion=direccion_,
                        autorizado=False,
                        cicloCaja=cicloCaja_,
                        cicloMensual=cicloMensual_,
                        identificador = user.nombre_apellido)
                        entrada.save()
                        #abrir barrera
                        rta = '#0' #Registro Socio Moroso
                except:
                    entrada = RegistroEstacionamiento(tipo='NOSOCIO',
                    lugar='ESTACIONAMIENTO',
                    noSocio=int(dato),
                    direccion=direccion_,
                    autorizado=True,
                    cicloCaja=cicloCaja_,
                    cicloMensual=cicloMensual_,
                    identificador = dato)
                    entrada.save()
                    rta = '#3' #NoSocio registrado
            else:
                try:
                    proveedor_ = Proveedor.objects.get(idProveedor = int(dato))
                    entrada = RegistroEstacionamiento(tipo='PROVEEDOR',
                    lugar='ESTACIONAMIENTO',
                    proveedor=proveedor_,
                    direccion=direccion_,
                    autorizado=True,
                    cicloCaja=cicloCaja_,
                    cicloMensual=cicloMensual_,
                    identificador = proveedor_.nombre_proveedor)
                    #abrir barrera
                    rta = '#1'
                except:
                    rta = '#4' #Error Proveedor no encontrado

        return HttpResponse(rta)

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
            estacionamiento = estacionamiento.filter(
                fecha__year=fecha[0],
                fecha__month=fecha[1],
                fecha__day=fecha[2]
            )

        if tiempo:
            tiempo = str(tiempo).split(':')
            estacionamiento = estacionamiento.filter(
                tiempo__hour=tiempo[0],
                tiempo__minute=tiempo[1]
            )

        table = HistorialEstacionamientoTable(estacionamiento)
        RequestConfig(request).configure(table)

        return render(
            request,
            'estacionamiento/historial.html',
            {'table': table, 'title': 'Historial'}
        )


def detalle_estacionamiento(request, id):
    obj = RegistroEstacionamiento.objects.get(id=id)
    form = EstacionamientoForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()

    if request.method == 'POST':
        return redirect('estacionamiento:historial')

    else:
        return render(request, 'estacionamiento/editar_historial.html',
                      {'form': form, 'title': 'Detalle historial'})
