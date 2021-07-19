import os
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


def postpone(function):
    def decorator(*args, **kwargs):
        t = Thread(target=function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()

    return decorator


@login_required
def lista_usuarios(request):
    return render(request, 'usuario/lista_usuarios.html',
                  {'title': 'Lista de socios'})


@login_required
def editar_usuario(request, id):
    obj = Persona.objects.get(id=id)
    form = PersonaForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()

    if request.method == 'POST':
        messages.success(request, 'Los datos fueron guardados con éxito')
        return redirect('usuario:lista')

    else:
        return render(request, 'usuario/editar_usuario.html',
                      {'form': form, 'title': 'Editar socio'})


@login_required
def historial(request):
    if request.method == 'GET':
        entradas = EntradaGeneral.objects.all()
        busqueda = request.GET.get('buscar')

        if busqueda:
            entradas = EntradaGeneral.objects.filter(
                Q(lugar__icontains=busqueda) |
                Q(tiempo__icontains=busqueda) |
                Q(persona__nombre_apellido__icontains=busqueda) |
                Q(persona__dni__icontains=busqueda)
            ).distinct()

        table = HistorialTable(entradas)
        RequestConfig(request).configure(table)

        return render(request, 'usuario/historial.html',
                      {'table': table, 'title': 'Historial'})


@login_required
def cargar_db(request):
    media_root = settings.MEDIA_ROOT
    location = os.path.join(media_root, 'saldos.csv')

    try:
        df = pd.read_csv(
            location,
            encoding='latin_1',
            error_bad_lines=False,
            names=list('abcdefghijklmnopqrstuv')
        )

    except:
        messages.warning(request, 'Ha habido un error al leer el archivo')
        return redirect('draganddrop:upload')

    df.drop('b', inplace=True, axis=1)
    df.drop('d', inplace=True, axis=1)

    for column in list('ghijklmnopqrstuv'):
        df.drop(str(column), inplace=True, axis=1)

    for ind in df.index:
        if not pd.isna(df['f'][ind]):
            df['e'][ind] = df['f'][ind]

    df.drop('f', inplace=True, axis=1)
    df = df.rename(columns={
        'a': 'NrSocio',
        'c': 'Socio',
        'e': 'Deuda'
    })
    if df['NrSocio'][5] != 'Composición de Saldos':
        messages.warning(request, 'El archivo subido es incorrecto')
        return redirect('draganddrop:upload')

    for row in range(10):
        df = df.drop(row)

    df = df.dropna(thresh=2)
    df['Deuda'] = df['Deuda'].fillna(0)

    cargar_db_async(df)

    messages.success(request, 'La carga de datos ha iniciado con éxito')
    return redirect('usuariosistema:home')


@postpone
def cargar_db_async(df):
    deudaMax = Deuda.objects.all().last().deuda
    listaUsuarios = []
    for ind in df.index:
        if float(str(df['Deuda'][ind]).replace(',', '')) > deudaMax:
            try:
                usuario = Persona.objects.get(nrSocio=int(df['NrSocio'][ind]))
                listaUsuarios.append(usuario.id)
                if usuario.general:
                    usuario.general = False
                    usuario.deuda = float(str(df['Deuda'][ind]).replace(',', ''))
                    usuario.save()

            except:
                partes_nombre = str(df['Socio'][ind]).strip().split(' ')
                name = ''
                for nombre in partes_nombre:
                    if nombre:
                        name += f'{nombre} '

                usuario = Persona(
                    nombre_apellido=name.strip(),
                    nrSocio=int(df['NrSocio'][ind]),
                    general=False,
                    deuda=float(str(df['Deuda'][ind]).replace(',', ''))
                )
                usuario.save()
                usuario = Persona.objects.get(nrSocio=int(df['NrSocio'][ind]))
                listaUsuarios.append(usuario.id)

        else:
            try:
                usuario = Persona.objects.get(nrSocio=int(df['NrSocio'][ind]))
                listaUsuarios.append(usuario.id)
                if not usuario.general:
                    usuario.general = True
                    usuario.deuda = float(str(df['Deuda'][ind]).replace(',', ''))
                    usuario.save()

            except:
                partes_nombre = str(df['Socio'][ind]).strip().split(' ')
                name = ''
                for nombre in partes_nombre:
                    if nombre:
                        name += f'{nombre} '

                usuario = Persona(
                    nombre_apellido=name.strip(),
                    nrSocio=int(df['NrSocio'][ind]),
                    general=True,
                    deuda=float(str(df['Deuda'][ind]).replace(',', ''))
                )
                usuario.save()
                usuario = Persona.objects.get(nrSocio=int(df['NrSocio'][ind]))
                listaUsuarios.append(usuario.id)

    personas = Persona.objects.all()
    for persona in personas:
        if persona.id not in listaUsuarios:
            persona.general = False
            persona.save()

    try:
        noSocio = personas.get(nombre_apellido='NOSOCIO')
        noSocio.general = True
        noSocio.save()

    except:
        noSocio = Persona(nrSocio=0, nombre_apellido='NOSOCIO',
                          general=True, deuda=0.0)
        noSocio.save()

    deudaMax = Deuda.objects.all().last().deudaEstacionamiento
    listaUsuarios = []
    for ind in df.index:
        if float(str(df['Deuda'][ind]).replace(',', '')) > deudaMax:
            try:
                usuario = Persona.objects.get(nrSocio=int(df['NrSocio'][ind]))
                listaUsuarios.append(usuario.id)
                if usuario.estacionamiento:
                    usuario.estacionamiento = False
                    usuario.deuda = float(str(df['Deuda'][ind]).replace(',', ''))
                    usuario.save()

            except:
                partes_nombre = str(df['Socio'][ind]).strip().split(' ')
                name = ''
                for nombre in partes_nombre:
                    if nombre:
                        name += f'{nombre} '

                usuario = Persona(
                    nombre_apellido=name.strip(),
                    nrSocio=int(df['NrSocio'][ind]),
                    estacionamiento=False,
                    deuda=float(str(df['Deuda'][ind]).replace(',', ''))
                )
                usuario.save()
                usuario = Persona.objects.get(nrSocio=int(df['NrSocio'][ind]))
                listaUsuarios.append(usuario.id)

        else:
            try:
                usuario = Persona.objects.get(nrSocio=int(df['NrSocio'][ind]))
                listaUsuarios.append(usuario.id)
                if not usuario.estacionamiento:
                    usuario.estacionamiento = True
                    usuario.deuda = float(str(df['Deuda'][ind]).replace(',', ''))
                    usuario.save()

            except:
                partes_nombre = str(df['Socio'][ind]).strip().split(' ')
                name = ''
                for nombre in partes_nombre:
                    if nombre:
                        name += f'{nombre} '

                usuario = Persona(
                    nombre_apellido=name.strip(),
                    nrSocio=int(df['NrSocio'][ind]),
                    estacionamiento=True,
                    deuda=float(str(df['Deuda'][ind]).replace(',', ''))
                )
                usuario.save()
                usuario = Persona.objects.get(nrSocio=int(df['NrSocio'][ind]))
                listaUsuarios.append(usuario.id)

    personas = Persona.objects.all()
    for persona in personas:
        if persona.id not in listaUsuarios:
            persona.estacionamiento = False
            persona.save()

    connection.close()


# La unica funcion de este view es la de que el codigo de js pueda hacer un
# a estos datos para renderizarlos en tiempo real sin tener que hacer otro
# request.
def fetch_usuarios(request):
    # Dentro del GET recibe como datos:
    page = request.GET.get('page')  # La pagina que quiere visualizar.
    filter_string = request.GET.get('filter-string')  # El string de filtro.

    # Separa el string para filtrar en un list con cada palabra ingresada.
    parsed_filter = filter_string.split(' ')

    personas = Persona.objects.all()
    # Filtra todos los socios con el string recibido por nombre de
    # socio.
    for filter in parsed_filter:
        personas = personas.filter(
            Q(nombre_apellido__icontains=filter) |
            Q(dni__icontains=filter),
            ~Q(nombre_apellido='NOSOCIO')
        ).order_by('nombre_apellido')

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
