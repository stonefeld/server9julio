from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
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
                entrada = EntradaGeneral(lugar='GENERAL', persona=user)
                entrada.save()
                rta = '1'

            else:
                rta = '0'

        except:
            rta = '-1'

        return HttpResponse(rta)

@login_required
def registro(request):
    return render(request, 'registroGeneral/registro_manual_seleccion.html', context={})

@login_required
def registro_socio(request):
    if request.method == 'POST':
        pks = request.POST.getlist('seleccion')
        for pk in pks:
            persona = Persona.objects.get(id=pk)
            if persona.general:
                entrada = EntradaGeneral(lugar='GENERAL', persona=persona)
                entrada.save()

            else:
                messages.error(request, f'El usuario ' +  persona.nombre_apellido + ' no tiene acceso.')

        if len(pks) > 1:
            messages.success(request, f'Usuarios registrados con éxito.')

        else:
            messages.success(request, f'Usuario registrado con éxito.')

        return redirect('usuariosistema:home')

    elif request.method == 'GET':
        persona = Persona.objects.all()
        busqueda = request.GET.get("buscar")

        if busqueda:
            persona = Persona.objects.filter(
                Q(nrSocio__icontains = busqueda) |
                Q(nombre_apellido__icontains = busqueda) |
                Q(nrTarjeta__icontains = busqueda) |
                Q(dni__icontains = busqueda)
            ).distinct()

        table = EntradaGeneralTable(persona.filter(general=True))
        RequestConfig(request).configure(table)

    return render(request, 'registroGeneral/registro_manual_socio.html', { 'table': table })

@login_required
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

