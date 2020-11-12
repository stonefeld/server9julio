from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Persona, Entrada
from django.db.models import Q


def tablaIngresos(request):
    if request.method == 'GET':
        entradas = Entrada.objects.all()
        busqueda = request.GET.get("buscar")

        if busqueda:
            entradas = Entrada.objects.filter(
                Q(lugar__icontains = busqueda) |
                Q(tiempo__icontains = busqueda) |
                Q(persona__nombre__icontains = busqueda) |
                Q(persona__apellido__icontains = busqueda) |
                Q(persona__dni__icontains = busqueda)
            ).distinct()
            

        return render(request, 'usuario/tablaIngresos.html', {'entradas': entradas})

