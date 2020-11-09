from django.shortcuts import render
from django.http import HttpResponse
from .models import Persona, Entrada

def respuesta(request):
    if request.method == 'GET':
        nrSocio = request.GET.get('nrSocio', '')
        lugar = request.GET.get('lugar', '')
        print(lugar,nrSocio)
        #try:  
        user = Persona.objects.get(nrSocio = nrSocio)
        print(user)
        if(lugar == '1'):
            lugar = 'general'
            entrada = Entrada(lugar = 'general',persona = user)
            entrada.save()
        rta = '1'
        #except:
            #rta = '-1'

        return HttpResponse("<h1>Valor correcto</h1><p>" + rta + "</p>")
