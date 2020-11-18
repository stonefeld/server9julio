from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from usuario.models import Persona
from registroGeneral.models import EntradaGeneral

def respuesta(request):
    if request.method == 'GET':
        nrTarjeta = request.GET.get('nrTarjeta', '')
        try:  
            user = Persona.objects.get(nrTarjeta = nrTarjeta)
            entrada = EntradaGeneral(lugar = 'estacionamiento',persona = user)
            entrada.save()
            rta = '1'
        except:
            rta = '-1'
            
        return HttpResponse("<h1>Valor correcto</h1><p>" + rta + "</p>")
