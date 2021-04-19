import csv
import os
from threading import Thread

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.timezone import localtime

from django_tables2 import RequestConfig

from .models import EntradaGeneral, Persona
from .tables import EntradaGeneralTable, EntradaGeneralNoAutorizadaTable


def postpone(function):
    def decorator(*args, **kwargs):
        t = Thread(target=function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()

    return decorator


def respuesta(request):
    if request.method == 'GET':
        nrTarjeta = request.GET.get('nrTarjeta', '')
        direccion = request.GET.get('direccion', '')
        try:
            user = Persona.objects.get(nrTarjeta=int(nrTarjeta))
            if user.general:
                if int(direccion) == 1:
                    entrada = EntradaGeneral(
                        lugar='GENERAL', persona=user,
                        direccion='SALIDA', autorizado=True
                    )

                else:
                    entrada = EntradaGeneral(
                        lugar='GENERAL', persona=user,
                        direccion='ENTRADA', autorizado=True
                    )

                entrada.save()
                rta = '#1'

            else:
                rta = '#0'

        except:
            rta = '#2'

        return HttpResponse(rta)


@login_required
def registro(request):
    return render(
        request,
        'registroGeneral/registro_manual_seleccion.html',
        {'title': 'Acceso manual'}
    )


@login_required
def registro_socio(request):
    if request.method == 'POST':
        direccion = request.POST.get('direccion')
        aceptar = request.POST.get('aceptar')
        rechazar = request.POST.get('rechazar')

        if direccion and not aceptar and not rechazar:
            persona_no_autorizada = []
            pks_no_autorizadas = ''
            pks = request.POST.getlist('seleccion')

            if len(pks) > 0:
                no_pasa = False
                for pk in pks:
                    try:
                        persona = Persona.objects.get(id=pk)
                        if persona.general:
                            entrada = EntradaGeneral(lugar='GENERAL', persona=persona, direccion=direccion, autorizado=True)
                            entrada.save()

                        else:
                            entrada = EntradaGeneral(lugar='GENERAL', persona=persona, direccion=direccion, autorizado=False)
                            persona_no_autorizada.append(persona)
                            pks_no_autorizadas += f'{pk},'
                            no_pasa = True

                    except:
                        return HttpResponse('Error')

                if not no_pasa:
                    if len(pks) > 1:
                        messages.success(request, 'Entradas registradas con éxito')

                    else:
                        messages.success(request, 'Entrada registrada con éxito')

                else:
                    table = EntradaGeneralNoAutorizadaTable(persona_no_autorizada)
                    RequestConfig(request).configure(table)

                    messages.warning(request, 'Los siguientes usuarios no están autoriazdos')
                    context = {
                        'table': table,
                        'title': 'Usuarios no autorizados',
                        'no_autorizado': True,
                        'direccion': f'{direccion},{pks_no_autorizadas}'
                    }
                    return render(request, 'registroGeneral/registro_manual_socio.html', context)

                cant = len(pks)
                socket_arduino(cant)
                return redirect('usuariosistema:home')

            else:
                persona = Persona.objects.all()
                busqueda = request.GET.get('buscar')

                if busqueda:
                    persona = Persona.objects.filter(
                        Q(nrSocio__icontains=busqueda) |
                        Q(nombre_apellido__icontains=busqueda) |
                        Q(nrTarjeta__icontains=busqueda) |
                        Q(dni__icontains=busqueda)
                    ).distinct()

                table = EntradaGeneralTable(persona.filter(~Q(nombre_apellido='NOSOCIO')))
                RequestConfig(request).configure(table)

                messages.warning(request, 'Debe seleccionar un usuario')
                context = {
                    'table': table,
                    'title': 'Acceso socio',
                    'no_autorizado': False
                }
                return render(request, 'registroGeneral/registro_manual_socio.html', context)

        elif not direccion and aceptar and not rechazar:
            pks = str(aceptar).split(',')
            pks.remove(pks[-1])

            direccion = pks[0]
            pks.remove(pks[0])

            for pk in pks:
                persona = Persona.objects.get(id=pk)
                entrada = EntradaGeneral(persona=persona, lugar='GENERAL', direccion=direccion, autorizado=False)
                entrada.save()

            messages.warning(request, 'Algunas entradas fueron registradas sin estar autorizadas')
            return redirect('usuariosistema:home')

        else:
            messages.warning(request, 'Algunas entradas no fueron registradas por no estar autorizadas')
            return redirect('usuariosistema:home')

    elif request.method == 'GET':
        persona = Persona.objects.all()
        busqueda = request.GET.get('buscar')

        if busqueda:
            persona = Persona.objects.filter(
                Q(nrSocio__icontains=busqueda) |
                Q(nombre_apellido__icontains=busqueda) |
                Q(nrTarjeta__icontains=busqueda) |
                Q(dni__icontains=busqueda)
            ).distinct()

        table = EntradaGeneralTable(
                persona.filter(~Q(nombre_apellido='NOSOCIO')))
        RequestConfig(request).configure(table)
        return render(
            request,
            'registroGeneral/registro_manual_socio.html',
            {'table': table, 'title': 'Acceso socio', 'no_autorizado': False}
        )


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
                    direccion=dire,
                    autorizado=True
                )
                entrada.save()

        except:
            messages.warning(request,
                             'Debe seleccionar la cantidad de personas')
            return render(
                request,
                'registroGeneral/registro_manual_nosocio.html',
                {'title': 'Acceso no socio'}
            )

        socket_arduino(cantidad)
        return redirect('usuariosistema:home')

    elif request.method == 'GET':
        return render(
            request,
            'registroGeneral/registro_manual_nosocio.html',
            {'title': 'Acceso no socio'}
        )


@login_required
def downloadHistory(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(['Persona', 'Lugar', 'Fecha y Hora',
                     'Dirección', 'Autorización'])

    for entrada in EntradaGeneral.objects.all().\
            values_list('persona', 'lugar',
                        'tiempo', 'direccion', 'autorizado'):
        entrada_list = list(entrada)
        entrada_list[0] = Persona.objects.\
            get(id=entrada_list[0]).nombre_apellido
        entrada_list[2] = localtime(entrada_list[2])
        writer.writerow(entrada_list)

    response['Content-Disposition'] = 'attachment; filename="historial.csv"'

    return response


@postpone
def socket_arduino(cantidad):
    base_dir = settings.BASE_DIR
    script_loc = os.path.join(base_dir, 'scripts/client.py')
    os.system(f'python3 {script_loc} abrir_tiempo {cantidad}')
