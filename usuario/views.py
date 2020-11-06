from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Persona, Entrada


# Create your views here.
def respuesta(request):
    if request.method == 'GET':
        rta = 'No existe'
        return HttpResponse("<h1>Valor correcto</h1><p>" + rta + "</p>")