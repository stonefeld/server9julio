from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required

import pandas as pd

from .models import Persona
from registroGeneral.models import EntradaGeneral

@login_required
def tablaIngresos(request):
    if request.method == 'GET':
        entradas = EntradaGeneral.objects.all()
        busqueda = request.GET.get("buscar")

        if busqueda:
            entradas = EntradaGeneral.objects.filter(
                Q(lugar__icontains = busqueda) |
                Q(tiempo__icontains = busqueda) |
                Q(persona__nombre_apellido__icontains = busqueda) |
                Q(persona__dni__icontains = busqueda)
            ).distinct()

        return render(request, 'usuario/tablaIngresos.html', { 'entradas': entradas })

