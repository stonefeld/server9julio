from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Persona, Entrada
from django.db.models import Q
import pandas as pd
from .forms import PersonaForm



def nrTarjeta(request):
    form = PersonaForm(request.POST or None)
    if form.is_valid():
        form.save()
    return render(request,'usuario/vincularTarjetas.html' )


def tablaIngresos(request):
    if request.method == 'GET':
        entradas = Entrada.objects.all()
        busqueda = request.GET.get("buscar")

        if busqueda:
            entradas = Entrada.objects.filter(
                Q(lugar__icontains = busqueda) |
                Q(tiempo__icontains = busqueda) |
                Q(persona__nombre__icontains = busqueda) |
                Q(persona__dni__icontains = busqueda)
            ).distinct()
            

        return render(request, 'usuario/tablaIngresos.html', {'entradas': entradas})


def cargarDB(request):
    deudaMax = 300
    listaUsuarios = [] #lista de usuarios actualizados
    location = 'C:/Users/User/Desktop/Servidor SAGVB/saldosPrueba.csv'
    #xlsx = pd.ExcelFile('C:/Users/User/Desktop/Servidor SAGVB/saldos.xls')
    df = pd.read_csv(location,encoding='unicode_escape',error_bad_lines=False, names = list('abcdefghijklmnopqrstuv'))#name=list('abecedario')
    df.drop('b', inplace=True, axis=1)
    df.drop('d', inplace=True, axis=1)
    for column in list('ghijklmnopqrstuv'):
        df.drop('%c'% (column), inplace=True, axis=1)
    for ind in df.index:
        if pd.isna(df['f'][ind]) == False:
            df['e'][ind] = df['f'][ind]
    df.drop('f', inplace=True, axis=1)
    df = df.rename(columns={'a':'NrSocio', 'c':'Socio','e':'Deuda'})
    for row in range(10):
        df = df.drop(row)
    df = df.dropna()
    for ind in df.index :
        if float((df['Deuda'][ind]).replace(',',''))>deudaMax:#si deuda es mayor a deudaMax .replace(',','')
            try:
                usuario = Persona.objects.get(nrSocio = int(df['NrSocio'][ind])) #cambiar la entrada a false
                listaUsuarios.append(usuario.id)
                if usuario.general == True: #cambiar entrada solo si es necesario cambiarlo
                    usuario.general = False
                    usuario.deuda = float((df['Deuda'][ind]).replace(',',''))
                    usuario.save()
            except:
                usuario = Persona(nombre = df['Socio'][ind], nrSocio = int(df['NrSocio'][ind]), general = False, deuda = float((df['Deuda'][ind]).replace(',','')) ) #sino existe el usuario crearlo
                usuario.save()
                usuario = Persona.objects.get(nrSocio = int(df['NrSocio'][ind]))
                listaUsuarios.append(usuario.id)
        else: #sino 
            try:
                usuario = Persona.objects.get(nrSocio = int(df['NrSocio'][ind])) #cambiar entrada a true
                listaUsuarios.append(usuario.id)
                if usuario.general == False:#cambiar entrada solo si es necesario cambiarlo
                    usuario.general = True
                    usuario.deuda = float((df['Deuda'][ind]).replace(',',''))
                    usuario.save()
            except :
                usuario = Persona(nombre = df['Socio'][ind], nrSocio = int(df['NrSocio'][ind]), general = True, deuda = float((df['Deuda'][ind]).replace(',','')) ) #sino existe el usuario crearlo
                usuario.save()
                usuario = Persona.objects.get(nrSocio = int(df['NrSocio'][ind]))
                listaUsuarios.append(usuario.id)

    personas = Persona.objects.all()
    for persona in personas:
        if persona.id not in listaUsuarios:
            persona.general = False
            persona.save()

    return HttpResponse("<h1>Valor correcto</h1>")