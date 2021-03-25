from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def menu_estacionamiento(request):
    return render(request, template_name='menu_estacionamiento/inicio_estacionamiento.html', context={})
    
def seleccionarCalendario(request):
    return render(request, template_name='menu_estacionamiento/calendario.html', context={})

def resumenTiempoReal(request):
    return render(request, template_name='menu_estacionamiento/resumen_tiempo.html', context={})

def proveedores(request):
    return render(request, template_name='menu_estacionamiento/proveedores.html', context={})

def historial(request):
    return render(request, template_name='menu_estacionamiento/historial.html', context={})