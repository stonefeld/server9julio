from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages

from django_tables2 import SingleTableView, RequestConfig

from .models import EntradaGeneral, Persona
from .forms import RegistroEntradaGeneralForms
from .tables import EntradaGeneralTable

def respuesta(request):
    if request.method == 'GET':
        nrTarjeta = request.GET.get('nrTarjeta', '')
        try:
            user = Persona.objects.get(nrTarjeta=nrTarjeta)
            if(user.general == True):
                entrada = EntradaGeneral(lugar='general', persona=user)
                entrada.save()
                rta = '1'

            else:
                rta = '0'

        except:
            rta = '-1'

        return HttpResponse(rta)

def registro(request):
    return render(request, 'registroGeneral/registro_manual_seleccion.html', context={})

def registro_socio(request):
    if request.method == 'POST':
        pks = request.POST.getlist('seleccion')
        for pk in pks:
            persona = Persona.objects.get(nrTarjeta=pk)
            if persona.general:
                entrada = EntradaGeneral(lugar='general', persona=persona)
                entrada.save()

            else:
                messages.error(request, f'El usuario ' +  persona.nombre_apellido + ' no tiene acceso.')

        return redirect('usuariosistema:home')

    else:
        table = EntradaGeneralTable(Persona.objects.filter(general=True))
        RequestConfig(request).configure(table)

    return render(request, 'registroGeneral/registro_manual_socio.html', { 'table': table })

def registro_nosocio(request):
    if request.method == 'POST':
        form = RegistroEntradaGeneralForms(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario registrado. Puede pasar')
            return redirect('usuariosistema:home')

    else:
        form = RegistroEntradaGeneralForms()
        obj = Persona.objects.all()

    return render(request, 'registroGeneral/registro_manual_nosocio.html', { 'form': form, 'obj': obj })

