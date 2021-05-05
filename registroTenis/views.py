from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from .models import EntradaTenis
from usuario.models import Persona


def respuesta(request):
    if request.method == 'GET':
        nrTarjeta = request.GET.get('nrTarjeta', '')
        direccion = request.GET.get('direccion', '')
        try:
            user = Persona.objects.get(nrTarjeta=int(nrTarjeta))
            if user.general:
                if int(direccion) == 1:
                    entrada = EntradaTenis(lugar='TENIS', persona=user, direccion='SALIDA', autorizado=True)

                else:
                    entrada = EntradaTenis(lugar='TENIS', persona=user, direccion='ENTRADA', autorizado=True)

                entrada.save()
                rta = '#1'

            else:
                rta = '#0'

        except:
            rta = '#2'

        return HttpResponse(rta)
