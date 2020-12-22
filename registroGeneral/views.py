import os, csv
from threading import Thread

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils.timezone import localtime

from django_tables2 import SingleTableView, RequestConfig

from .models import EntradaGeneral, Persona
from .forms import RegistroEntradaGeneralForms
from .tables import EntradaGeneralTable

def postpone(function):
    def decorator(*args, **kwargs):
        t = Thread(target=function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()

    return decorator

def respuesta(request):
    if request.method == 'GET':
        nrTarjeta = request.GET.get('nrTarjeta', '')
        direccion = request.GET.get('direccion','')
        try:
            user = Persona.objects.get(nrTarjeta=int(nrTarjeta))
            if(user.general == True):
                if int(direccion) == 1:
                    entrada = EntradaGeneral(lugar='GENERAL', persona=user, direccion='SALIDA')

                else:
                    entrada = EntradaGeneral(lugar='GENERAL', persona=user, direccion='ENTRADA')

                entrada.save()
                rta = '#1'

            else:
                rta = '#0'

        except:
            rta = '#2'

        return HttpResponse(rta)

@login_required
def registro(request):
    return render(request, 'registroGeneral/registro_manual_seleccion.html', context={})

@login_required
def registro_socio(request):
    if request.method == 'POST':
        pks = request.POST.getlist('seleccion')
        if len(pks) > 0:
            direccion = request.POST.getlist('direccion')
            dire = str(direccion[0])
            for pk in pks:
                try:
                    persona = Persona.objects.get(id=pk)
                    if persona.general:
                        entrada = EntradaGeneral(lugar='GENERAL', persona=persona, direccion=dire)
                        entrada.save()
                        no_pasa = False

                    else:
                        messages.warning(request, f'El usuario ' +  persona.nombre_apellido + ' no tiene acceso.')
                        no_pasa = True

                except:
                    return HttpResponse('Error')

            if not no_pasa:
                if len(pks) > 1:
                    messages.success(request, f'Entradas registradas con éxito.')

                else:
                    messages.success(request, f'Entrada registrada con éxito.')

            cant = len(pks)
            socket_arduino(cant)
            return redirect('usuariosistema:home')

        else:
            persona = Persona.objects.all()
            busqueda = request.GET.get('buscar')

            if busqueda:
                persona = Persona.objects.filter(
                    Q(nrSocio__icontains = busqueda) |
                    Q(nombre_apellido__icontains = busqueda) |
                    Q(nrTarjeta__icontains = busqueda) |
                    Q(dni__icontains = busqueda)
                ).distinct()

            table = EntradaGeneralTable(persona.filter(~Q(nombre_apellido='NOSOCIO')))
            RequestConfig(request).configure(table)
            messages.warning(request, f'Debe seleccionar un usuario')
            return render(request, 'registroGeneral/registro_manual_socio.html', { 'table': table })

    elif request.method == 'GET':
        persona = Persona.objects.all()
        busqueda = request.GET.get('buscar')

        if busqueda:
            persona = Persona.objects.filter(
                Q(nrSocio__icontains = busqueda) |
                Q(nombre_apellido__icontains = busqueda) |
                Q(nrTarjeta__icontains = busqueda) |
                Q(dni__icontains = busqueda)
            ).distinct()

        table = EntradaGeneralTable(persona.filter(~Q(nombre_apellido='NOSOCIO')))
        RequestConfig(request).configure(table)
        return render(request, 'registroGeneral/registro_manual_socio.html', { 'table': table })

@login_required
def registro_nosocio(request):
    if request.method == 'POST':
        cantidad = request.POST.getlist('cantidad')
        direccion = request.POST.getlist('direccion')

        try:
            cantidad = int(cantidad[0])
            dire = str(direccion[0])
            for i in range(cantidad):
                entrada = EntradaGeneral(
                    lugar='GENERAL',
                    persona=Persona.objects.get(nombre_apellido='NOSOCIO'),
                    direccion=dire
                )
                entrada.save()

        except:
            messages.warning(request, f'Debe seleccionar la cantidad de personas')
            return render(request, 'registroGeneral/registro_manual_nosocio.html', context={})


        socket_arduino(cantidad)
        return redirect('usuariosistema:home')

    else:
        return render(request, 'registroGeneral/registro_manual_nosocio.html', context={})

@login_required
def downloadHistory(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(['Persona', 'Lugar', 'Fecha y Hora', 'Dirección'])

    for entrada in EntradaGeneral.objects.all().values_list('persona', 'lugar', 'tiempo', 'direccion'):
        entrada_list = list(entrada)
        entrada_list[0] = Persona.objects.get(id=entrada_list[0]).nombre_apellido
        entrada_list[2] = localtime(entrada_list[2])
        writer.writerow(entrada_list)

    response['Content-Disposition'] = 'attachment; filename="historial.csv"'

    return response

@postpone
def socket_arduino(cantidad):
    base_dir = settings.BASE_DIR
    script_loc = os.path.join(base_dir, 'scripts/client.py')
    os.system('python3 ' + script_loc + ' abrir_tiempo ' + str(cantidad))

