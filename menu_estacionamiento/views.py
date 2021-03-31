from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def menu_estacionamiento(request):
    return render(
        request,
        template_name='menu_estacionamiento/inicio_estacionamiento.html',
        context={}
    )


@login_required
def seleccionarCalendario(request):
    return render(
        request,
        template_name='menu_estacionamiento/calendario.html',
        context={}
    )


@login_required
def resumenTiempoReal(request):
    return render(
        request,
        template_name='menu_estacionamiento/resumen_tiempo.html',
        context={}
    )


@login_required
def proveedores(request):
    return render(
        request,
        template_name='menu_estacionamiento/proveedores.html',
        context={}
    )


@login_required
def historial(request):
    return render(
        request,
        template_name='menu_estacionamiento/historial.html',
        context={}
    )
