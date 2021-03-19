import os
from threading import Thread

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.models import Q
from django.shortcuts import render, redirect

from django_tables2 import RequestConfig

import pandas as pd

from .models import Persona, Deuda
from .forms import PersonaForm
from .tables import PersonaTable
from registroGeneral.models import EntradaGeneral
from registroGeneral.tables import HistorialTable


def postpone(function):
    def decorator(*args, **kwargs):
        t = Thread(target=function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()

    return decorator


@login_required
def listaUsuarios(request):
    if request.method == 'GET':
        persona = Persona.objects.all()
        busqueda = request.GET.get('buscar')

        if busqueda:
            persona = Persona.objects.filter(
                Q(nrSocio__icontains=busqueda) |
                Q(nombre_apellido__icontains=busqueda) |
                Q(nrTarjeta__icontains=busqueda) |
                Q(dni__icontains=busqueda)
            ).distinct()

        table = PersonaTable(persona.filter(~Q(nombre_apellido='NOSOCIO')))
        RequestConfig(request).configure(table)

        return render(request, 'usuario/lista_usuarios.html',
                      {'table': table, 'title': 'Lista de usuarios'})


@login_required
def editarUsuario(request, id):
    obj = Persona.objects.get(id=id)
    form = PersonaForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()

    if request.method == 'POST':
        return redirect('usuariosistema:home')

    else:
        return render(request,'usuario/editar_usuario.html',
                      {'form': form, 'title': 'Editar usuario'})


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
def cargarDB(request):
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
        df.drop(f'{column}', inplace=True, axis=1)

    for ind in df.index:
        if pd.isna(df['f'][ind]):
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

    df = df.dropna()

    cargarDBAsync(df)

    messages.success(request, 'La carga de datos ha iniciado con éxito')
    return redirect('usuariosistema:home')


@postpone
def cargarDBAsync(df):
    deudaMax = Deuda.objects.all().last().deuda
    listaUsuarios = []

    for ind in df.index:
        if float((df['Deuda'][ind]).replace(',', '')) > deudaMax:
            try:
                usuario = Persona.objects.get(nrSocio=int(df['NrSocio'][ind]))
                listaUsuarios.append(usuario.id)
                if usuario.general:
                    usuario.general = False
                    usuario.deuda = float((df['Deuda'][ind]).replace(',', ''))
                    usuario.save()

            except:
                usuario = Persona(
                    nombre_apellido=str(df['Socio'][ind]).strip(),
                    nrSocio=int(df['NrSocio'][ind]),
                    general=False,
                    deuda=float((df['Deuda'][ind]).replace(',', ''))
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
                    usuario.deuda = float((df['Deuda'][ind]).replace(',', ''))
                    usuario.save()

            except:
                usuario = Persona(
                    nombre_apellido=str(df['Socio'][ind]).strip(),
                    nrSocio=int(df['NrSocio'][ind]),
                    general=True,
                    deuda=float((df['Deuda'][ind]).replace(',', ''))
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

    connection.close()
