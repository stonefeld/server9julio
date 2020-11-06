from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Persona, Entrada


# Create your views here.
def respuesta(request):
    if request.method == 'GET':
        nrSocio = request.GET.get('nrSocio', '')
        lugar = request.GET.get('lugar', '')
        print(lugar,nrSocio)
        try:  
            user = Persona.objects.get(nrSocio = nrSocio)
            if(lugar == '1'): 
                print(user)
                lugar = 'general'
                entrada = Entrada(lugar = 'general',persona = user)
                entrada.save()
                print(user.general)
                if(user.general == True):
                    rta = '1'
                else:
                    rta = '0'
            elif(lugar == '2'):
                lugar == 'tenis'
                entrada = Entrada(lugar = 'tenis', persona = user)
                entrada.save()
                if(user.tenis == True):
                    rta = '1'
                else:
                    rta = '0'
            elif(lugar == '3'):
                lugar = 'piletas'
                entrada = Entrada(lugar = 'piletas', persona = user)
                entrada.save()
                if(user.pileta == True):
                    rta = '1'
                else:
                    rta = '0'
            else:
                rta = '0'
     
        except:
            rta = '-1'

        return HttpResponse("<h1>Valor correcto</h1><p>" + rta + "</p>")