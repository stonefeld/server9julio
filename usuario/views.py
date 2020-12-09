from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages

from django_tables2 import SingleTableView, RequestConfig

import pandas as pd

from .models import Persona
from .forms import PersonaForm
from registroGeneral.models import EntradaGeneral
from registroGeneral.tables import EntradaGeneralTable

@login_required
def vincular(request, id):
    obj = Persona.objects.get(id=id)
    form = PersonaForm(request.POST or None , instance=obj)
    if form.is_valid():
        form.save()

    if request.method == 'POST':
        return redirect('usuariosistema:home')

    else:
        return render(request,'usuario/vinculacion.html', {'form': form })

@login_required
def nrTarjeta(request):
    if request.method == 'POST':
        pks = request.POST.getlist('seleccion')
        persona = Persona.objects.get(id=pks[0])
        return redirect(persona.get_absolute_url())

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

        table = EntradaGeneralTable(persona.filter(~Q(nombre_apellido='NOSOCIO'), general=True))
        RequestConfig(request).configure(table)
        return render(request, 'usuario/vincularTarjetas.html', { 'table': table })

@login_required
def tablaIngresos(request):
    if request.method == 'GET':
        entradas = EntradaGeneral.objects.all()
        busqueda = request.GET.get('buscar')

        if busqueda:
            entradas = EntradaGeneral.objects.filter(
                Q(lugar__icontains = busqueda) |
                Q(tiempo__icontains = busqueda) |
                Q(persona__nombre_apellido__icontains = busqueda) |
                Q(persona__dni__icontains = busqueda)
            ).distinct()

        return render(request, 'usuario/tablaIngresos.html', { 'entradas': entradas })

@login_required
def cargarDB(request):
    deudaMax = 300
    location = './media/saldos.csv'

    try:
        df = pd.read_csv(
            location,
            encoding='latin_1',
            error_bad_lines=False,
            names=list('abcdefghijklmnopqrstuv')
        )

    except :
        return HttpResponse('Error en la lectura del archivo')

    df.drop('b', inplace=True, axis=1)
    df.drop('d', inplace=True, axis=1)

    for column in list('ghijklmnopqrstuv'):
        df.drop('%c'% (column), inplace=True, axis=1)

    for ind in df.index:
        if pd.isna(df['f'][ind]) == False:
            df['e'][ind] = df['f'][ind]

    df.drop('f', inplace=True, axis=1)
    df = df.rename(columns={
        'a': 'NrSocio',
        'c': 'Socio',
        'e': 'Deuda'
    })

    if df['NrSocio'][5] != 'Composición de Saldos':
        return HttpResponse('error archivo incorrecto')

    for row in range(10):
        df = df.drop(row)

    df = df.dropna()

    listaUsuarios = []
    noise = 1

    for ind in df.index:
        if 'PROVISORIO' not in str(df['Socio'][ind]):
            if float((df['Deuda'][ind]).replace(',', '')) > deudaMax:
                try:
                    usuario = Persona.objects.get(nrSocio=int(df['NrSocio'][ind]))
                    listaUsuarios.append(usuario.id)
                    if usuario.general == True:
                        usuario.general = False
                        usuario.deuda = float((df['Deuda'][ind]).replace(',', ''))
                        usuario.save()

                except:
                    usuario = Persona(
                        nombre_apellido=df['Socio'][ind],
                        nrSocio=int(df['NrSocio'][ind]),
                        general=False,
                        deuda=float((df['Deuda'][ind]).replace(',',''))
                    )
                    usuario.save()
                    usuario = Persona.objects.get(nrSocio=int(df['NrSocio'][ind]))
                    listaUsuarios.append(usuario.id)

            else:
                try:
                    usuario = Persona.objects.get(nrSocio=int(df['NrSocio'][ind]))
                    listaUsuarios.append(usuario.id)
                    if usuario.general == False:
                        usuario.general = True
                        usuario.deuda = float((df['Deuda'][ind]).replace(',', ''))
                        usuario.save()

                except:
                    usuario = Persona(
                        nombre_apellido=df['Socio'][ind],
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
        noSocio = Persona(nrSocio=0, nombre_apellido='NOSOCIO', general=True, deuda=0.0)
        noSocio.save()

    return redirect('usuariosistema:home')
