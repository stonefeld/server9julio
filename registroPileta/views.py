from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required

from usuario.models import Persona
from .models import EntradaPileta

def respuesta(request):
    if request.method == 'GET':
        nrTarjeta = request.GET.get('nrTarjeta', '')
        try:
            user = Persona.objects.get(nrTarjeta=nrTarjeta)
            if(user.general == True):
                entrada = Entrada(lugar='pileta', persona=user)
                entrada.save()
                rta = '1'
            else:
                rta = '0'
        except:
            rta = '-1'

        return HttpResponse("<h1>Valor correcto</h1><p>" + rta + "</p>")
