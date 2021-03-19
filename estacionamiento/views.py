from django.shortcuts import render
from threading import Thread
from .models import RegistroEstacionamiento, Proveedor, Cobros, CicloCaja, CicloMensual, Persona
import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.timezone import localtime

from django_tables2 import SingleTableView, RequestConfig

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

def respuesta(request):
    if request.method == 'GET':
        tipo = request.GET.get('tipo', '') #el tipo de dato que vamos a recibir (NrTarjeta=0/DNI=1/Proveedor=2)
        dato = request.GET.get('dato', '') #el dato
        direccion_ = request.GET.get('direccion', '') 
        cicloCaja_ = CicloCaja.objects.all().last().cicloCaja
        cicloMensual_ = CicloMensual.objects.all().last().cicloMensual
        if int(direccion_) == 1:
            direccion_ = 'SALIDA'
        else:
            direccion_ = 'ENTRADA'
        if int(tipo) == 0:
            try:
                user = Persona.objects.get(nrTarjeta=int(dato))
                if user.general == True:
                    entrada = RegistroEstacionamiento(tipo='SOCIO',lugar='ESTACIONAMIENTO', persona=user, direccion=direccion_, autorizado=True, cicloCaja=cicloCaja_, cicloMensual=cicloMensual_)
                    entrada.save()
                    #abrir barrera
                    rta = '#1'
                else:
                    entrada = RegistroEstacionamiento(tipo='SOCIO-MOROSO',lugar='ESTACIONAMIENTO', persona=user, direccion=direccion_, autorizado=False, cicloCaja=cicloCaja_, cicloMensual=cicloMensual_)
                    entrada.save()
                    rta = '#0' #Registro Socio Moroso

            except:
                rta = '#2' #el usuario No existe
        elif int(tipo) == 1:
            try:
                user = Persona.objects.get(dni = int(dato))
                if user.general == True:
                    entrada = RegistroEstacionamiento(tipo='SOCIO',lugar='ESTACIONAMIENTO', persona=user, direccion=direccion_, autorizado=True, cicloCaja=cicloCaja_, cicloMensual=cicloMensual_)
                    entrada.save()
                    rta = '#1'
                else:
                    entrada = RegistroEstacionamiento(tipo='SOCIO-MOROSO',lugar='ESTACIONAMIENTO', persona=user, direccion=direccion_, autorizado=False, cicloCaja=cicloCaja_, cicloMensual=cicloMensual_)
                    entrada.save()
                    #abrir barrera
                    rta = '#0' #Registro Socio Moroso
            except:
                entrada = RegistroEstacionamiento(tipo='NOSOCIO',lugar='ESTACIONAMIENTO', noSocio=int(dato), direccion=direccion_, autorizado=True, cicloCaja=cicloCaja_, cicloMensual=cicloMensual_)
                entrada.save()
                rta = '#3' #NoSocio registrado
        else:
            try:
                proveedor_ = Proveedor.objects.get(idProveedor = int(dato))
                entrada = RegistroEstacionamiento(tipo='PROVEEDOR',lugar='ESTACIONAMIENTO', proveedor=proveedor_, direccion=direccion_, autorizado=True, cicloCaja=cicloCaja_, cicloMensual=cicloMensual_)
                #abrir barrera
                rta = '#1'
            except:
                rta = '#4' #Error Proveedor no encontrado

        return HttpResponse(rta)
