import os
import re
from threading import Thread

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect

from django_tables2 import RequestConfig

import pandas as pd

from .models import Persona, Deuda
from .forms import PersonaForm
from registroGeneral.models import EntradaGeneral
from registroGeneral.tables import HistorialTable
from estacionamiento.models import RegistroEstacionamiento
from estacionamiento.views import funcion_cobros


def postpone(function):
    def decorator(*args, **kwargs):
        t = Thread(target=function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()

    return decorator


@login_required
def lista_usuarios(request):
    return render(request, 'usuario/lista_usuarios.html', {'title': 'Lista de socios'})


@login_required
def lista_proveedores(request):
    return render(request, 'usuario/lista_proveedores.html', {'title': 'Lista de proveedores'})


@login_required
def editar_usuario(request, id):
    obj = Persona.objects.get(id=id)
    form = PersonaForm(request.POST or None, instance=obj)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            estacionamiento = RegistroEstacionamiento.objects.filter(
                Q(identificador=form.cleaned_data['dni']) |
                Q(noSocio=form.cleaned_data['dni']),
                Q(direccion='ENTRADA'),
                Q(tipo='NOSOCIO')
            ).last()

            if estacionamiento and funcion_cobros(estacionamiento.noSocio) != 'SI':
                estacionamiento.persona = obj
                if obj.estacionamiento:
                    estacionamiento.tipo = 'SOCIO'
                    message = ' Se modificaron los datos del DNI del socio. El socio no tiene deuda y no debe abonar tarifa ni regularizar la deuda.'
                    if message not in estacionamiento.mensaje:
                        estacionamiento.mensaje += message

                else:
                    estacionamiento.tipo = 'SOCIO-MOROSO'
                    message = ' Se modificaron los datos del DNI del socio. El socio tiene deuda y debe regularizarla o abonar la tarifa correspondiente.'
                    if message not in estacionamiento.mensaje:
                        estacionamiento.mensaje += message

                estacionamiento.save()
                messages.info(request, '1 registro del estacionamiento fue modificado')

        messages.success(request, 'Los datos fueron guardados con éxito')
        return redirect('usuario:lista')

    else:
        return render(request, 'usuario/editar_usuario.html', {'form': form, 'title': 'Editar socio'})


@login_required
def historial(request):
    if request.method == 'GET':
        entradas = EntradaGeneral.objects.all()
        busqueda = request.GET.get('buscar')
        fecha_inicio = request.GET.get('fecha-inicio')
        fecha_final = request.GET.get('fecha-final')

        context = {'title': 'Historial'}

        if busqueda:
            entradas = entradas.filter(
                Q(lugar__icontains=busqueda) |
                Q(tiempo__icontains=busqueda) |
                Q(persona__nombre_apellido__icontains=busqueda) |
                Q(persona__dni__icontains=busqueda)
            ).distinct()

        if fecha_inicio and fecha_final:
            entradas = entradas.filter(tiempo__date__range=(fecha_inicio, fecha_final)).distinct()
            context['finicio'] = fecha_inicio
            context['ffinal'] = fecha_final

        table = HistorialTable(entradas)
        RequestConfig(request).configure(table)

        context['table'] = table

        return render(request, 'usuario/historial.html', context)


@login_required
def cargar_db(request):
    media_root = settings.MEDIA_ROOT
    location = os.path.join(media_root, 'saldos.xls')

    try:
        df = pd.read_excel(
            location,
            names=list('abcdefghijklmnopqrstuvwxyzaaa')
        )

    except Exception:
        messages.warning(request, 'Ha habido un error. Suba el archivo de datos con extension .xls')
        return redirect('draganddrop:upload')

    for col in list('cdefghijklmnopqrsy'):
        df.drop(col, inplace=True, axis=1)

    df.drop('a.1', inplace=True, axis=1)
    df.drop('a.2', inplace=True, axis=1)
    df.drop('a.3', inplace=True, axis=1)

    df = df.rename(columns={
        'a': 'NrSocio',
        'b': 'Socio',
        't': 'N-1',
        'u': 'N-2',
        'v': 'N-3',
        'w': 'Anterior',
        'x': 'Punitorios',
        'z': 'TipoDebito'
    })

    if df['NrSocio'][0] != 'Socio' or df['Socio'][0] != 'Nombre':
        messages.warning(request, 'El archivo subido es incorrecto')
        return redirect('draganddrop:upload')

    df = df.drop(0)

    cargar_db_async(df)

    messages.success(request, 'La carga de datos ha iniciado con éxito')
    return redirect('usuariosistema:home')


@postpone
def cargar_db_async(df):
    deuda_max_gen = Deuda.objects.all().last().deuda
    deuda_max_est = Deuda.objects.all().last().deudaEstacionamiento
    lista_usr = []

    for ind in df.index:
        deuda = float(df['N-2'][ind] + df['N-3'][ind] + df['Anterior'][ind] + df['Punitorios'][ind])
        if df['TipoDebito'][ind] == 'Sin Débito.':
            deuda += df['N-1'][ind]

        general = True
        if deuda > deuda_max_gen:
            general = False

        estacionamiento = True
        if deuda > deuda_max_est:
            estacionamiento = False

        nr_socio = int(df['NrSocio'][ind])

        try:
            usr = Persona.objects.get(nrSocio=nr_socio)
            lista_usr.append(usr.id)
            usr.general = general
            usr.estacionamiento = estacionamiento
            usr.deuda = deuda
            usr.save()

        except Exception:
            name = re.sub(' +', ' ', str(df['Socio'][ind]).strip())
            usr = Persona(
                nombre_apellido=name,
                nrSocio=nr_socio,
                general=general,
                estacionamiento=estacionamiento,
                deuda=deuda
            ).save()
            usr = Persona.objects.get(nrSocio=nr_socio)
            lista_usr.append(usr.id)

    personas = Persona.objects.all()
    for persona in personas:
        if persona.id not in lista_usr:
            persona.general = False
            persona.estacionamiento = False
            persona.save(no_existe=True)

    name = 'NOSOCIO'
    try:
        no_socio = personas.get(nombre_apellido=name)
        no_socio.general = True
        no_socio.estacionamiento = True
        no_socio.save()

    except Exception:
        Persona(nrSocio=0, nombre_apellido=name, general=True, estacionamiento=True, deuda=0.0).save()

    connection.close()


# La unica funcion de este view es la de que el codigo de js pueda hacer un
# a estos datos para renderizarlos en tiempo real sin tener que hacer otro
# request.
def fetch_usuarios(request):
    # dentro del GET recibe como datos:
    page = request.GET.get('page')  # la pagina que quiere visualizar.
    filter_string = request.GET.get('filter-string')  # el string de filtro.
    order_by = request.GET.get('order-by')

    # Separa el string para filtrar en un list con cada palabra ingresada.
    parsed_filter = filter_string.split(' ')

    personas = Persona.objects.all()
    # Filtra todos los socios con el string recibido por nombre de
    # socio.
    for filter in parsed_filter:
        personas = personas.filter(
            Q(nombre_apellido__icontains=filter) |
            Q(dni__icontains=filter) |
            Q(nrSocio__icontains=filter),
            ~Q(nombre_apellido='NOSOCIO')
        ).order_by(order_by)

    # Realiza la paginacion de los datos con un maximo de 20 proveedores por
    # pagina y especifica la pagina que quiere visualizar.
    paginated = Paginator(list(personas.values()), 20)
    personas = paginated.page(page).object_list

    # Agrega al json de respuesta los datos para que el codigo de js sepa
    # si la pagina que esta visualizandose tiene pagina siguiente o anterior.
    personas.append({
        'has_previous': paginated.page(page).has_previous(),
        'has_next': paginated.page(page).has_next()
    })

    # Devuelve la respuesta en forma de json especificando el 'safe=False'
    # para evitar tener problemas de CORS.
    return JsonResponse(personas, safe=False)
