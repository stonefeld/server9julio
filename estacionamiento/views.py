from threading import Thread
import os

from django.conf import settings
from django.http import HttpResponse
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


def respuesta(request):
    if request.method == 'GET':
        tipo = request.GET.get('tipo', '')  # el tipo de dato que vamos a recibir (NrTarjeta=0/DNI=1/Proveedor=2)
        dato = request.GET.get('dato', '')  # el dato
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
                if user.general:
                    entrada = RegistroEstacionamiento(
                        identificador=user,
                        tipo='SOCIO',
                        lugar='ESTACIONAMIENTO',
                        persona=user,
                        direccion=direccion_,
                        autorizado=True,
                        cicloCaja=cicloCaja_,
                        cicloMensual=cicloMensual_
                    )
                    entrada.save()
                    # abrir barrera
                    rta = '#1'

                else:
                    entrada = RegistroEstacionamiento(
                        identificador=user,
                        tipo='SOCIO-MOROSO',
                        lugar='ESTACIONAMIENTO',
                        persona=user,
                        direccion=direccion_,
                        autorizado=False,
                        cicloCaja=cicloCaja_,
                        cicloMensual=cicloMensual_
                    )
                    entrada.save()
                    rta = '#0'  # Registro Socio Moroso

            except:
                rta = '#2'  # el usuario No existe

        elif int(tipo) == 1:
            try:
                user = Persona.objects.get(dni=int(dato))
                if user.general:
                    entrada = RegistroEstacionamiento(
                        identificador=user,
                        tipo='SOCIO',
                        lugar='ESTACIONAMIENTO',
                        persona=user,
                        direccion=direccion_,
                        autorizado=True,
                        cicloCaja=cicloCaja_,
                        cicloMensual=cicloMensual_
                    )
                    entrada.save()
                    rta = '#1'

                else:
                    entrada = RegistroEstacionamiento(
                        identificador=user,
                        tipo='SOCIO-MOROSO',
                        lugar='ESTACIONAMIENTO',
                        persona=user,
                        direccion=direccion_,
                        autorizado=False,
                        cicloCaja=cicloCaja_,
                        cicloMensual=cicloMensual_
                    )
                    entrada.save()
                    # abrir barrera
                    rta = '#0'  # Registro Socio Moroso

            except:
                entrada = RegistroEstacionamiento(
                    identificador=int(dato),
                    tipo='NOSOCIO',
                    lugar='ESTACIONAMIENTO',
                    noSocio=int(dato),
                    direccion=direccion_,
                    autorizado=True,
                    cicloCaja=cicloCaja_,
                    cicloMensual=cicloMensual_
                )
                entrada.save()
                rta = '#3'  # NoSocio registrado

        else:
            try:
                proveedor_ = Proveedor.objects.get(idProveedor=int(dato))
                entrada = RegistroEstacionamiento(
                    identificador=proveedor_,
                    tipo='PROVEEDOR',
                    lugar='ESTACIONAMIENTO',
                    proveedor=proveedor_,
                    direccion=direccion_,
                    autorizado=True,
                    cicloCaja=cicloCaja_,
                    cicloMensual=cicloMensual_
                )
                # abrir barrera
                rta = '#1'

            except:
                rta = '#4'  # Error Proveedor no encontrado

        return HttpResponse(rta)


def historial_estacionamiento(request):
    if request.method == 'GET':
        estacionamiento = RegistroEstacionamiento.objects.all()
        table = HistorialEstacionamientoTable(estacionamiento)
        RequestConfig(request).configure(table)

        return render(
            request,
            'registroGeneral/registro_manual_socio.html',
            {'table': table}
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
