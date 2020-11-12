from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import EntradaGeneral
from .forms import RegistroEntradaGeneralForms

def respuesta(request):
    if request.method == 'GET':
        nrTarjeta = request.GET.get('nrTarjeta', '')
        try:
            user = EntradaGeneral.objects.all().persona.get(nrTarjeta=nrTarjeta)
            if(user.general == True):
                entrada = Entrada(lugar='general',persona=user)
                entrada.save()
                rta = '1'

            else:
                rta = '0'

        except:
            rta = '-1'

        return HttpResponse("<h1>Valor correcto</h1><p>" + rta + "</p>")

def registro(request):
    if request.method == 'POST':
        form = RegistroEntradaGeneralForms(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario registrado. Puede pasar')
            return redirect('usuariosistema:home')

    else:
        form = RegistroEntradaGeneralForms()

    return render(request, 'registroGeneral/registro_manual.html', { 'form': form })
