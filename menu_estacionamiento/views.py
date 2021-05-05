from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from estacionamiento.models import (
    RegistroEstacionamiento, Proveedor,
    CicloCaja, CicloMensual, Persona, CicloAnual, Cobros, Estacionado, Proveedor
)
from django_tables2 import RequestConfig
from estacionamiento.tables import EstacionadosTable, ProveedoresTable



@login_required
def menu_estacionamiento(request):
    return render(
        request,
        template_name='menu_estacionamiento/inicio_estacionamiento.html',
        context={}
    )


@login_required
def seleccionarCalendario(request):
    context = {}
    if request.method == 'POST':
        tarifas = request.POST.get('valorTarifaNormal','valorTarifaNormal2','valorTarifaNormal3')
        print(tarifas)
        try:
            deudaMax = request.POST.get('deuda')
            deuda = Deuda(deuda=deudaMax)

            media_root = settings.MEDIA_ROOT
            location = os.path.join(media_root, 'saldos.csv')

            if os.path.exists(location):
                os.remove(location)

            try:
                uploaded_file = request.FILES['file']
                fs = FileSystemStorage()
                name = fs.save('saldos.csv', uploaded_file)
                context['url'] = fs.url(name)
                deuda.save()

                return redirect('usuario:cargarDB')

            except:
                context = {
                    'deuda': str(Deuda.objects.all().last().deuda),
                    'title': 'Subir archivos'
                }
                messages.warning(request, 'Debe subir un archivo')

        except:
            context = {
                'deuda': str(Deuda.objects.all().last().deuda),
                'title': 'Subir archivos'
            }
            messages.warning(request, 'Debe especificar una deuda máxima')

        
    
    return render(
        request,
        template_name='menu_estacionamiento/calendario.html',
        context={}
        )



@login_required
def resumenTiempoReal(request):
    if request.method == 'GET':
        estacionamiento = Estacionado.objects.all()
        
        
        busqueda = request.GET.get('buscar')
        fecha = request.GET.get('fecha')
        tiempo = request.GET.get('tiempo')

        if busqueda:
            estacionamiento = estacionamiento.filter(
                Q(registroEstacionamiento__identificador__icontains=busqueda),
            ).distinct()

        if fecha:
            fecha = str(fecha).split('-')
            fecha = date(int(fecha[0]), int(fecha[1]), int(fecha[2]))
            estacionamiento = estacionamiento.filter(
                registroEstacionamiento__tiempo__date=fecha
            )

        if tiempo:
            tiempo = str(tiempo).split(':')
            tiempo = time(int(tiempo[0]), int(tiempo[1]))
            estacionamiento = estacionamiento.filter(
                registroEstacionamiento__tiempo__hour=tiempo.hour,
                registroEstacionamiento__tiempo__minute=tiempo.minute
            )
        table = EstacionadosTable(estacionamiento)
        RequestConfig(request).configure(table)
        return render(
            request,
            'menu_estacionamiento/resumen_tiempo.html',
            {'table': table, 'title': 'Historial'}
        )
    return render(
        request,
        template_name='menu_estacionamiento/resumen_tiempo.html',
        context={}
    )


@login_required
def proveedores(request):
    proveedores = Proveedor.objects.all()
    table = ProveedoresTable(proveedores)
    RequestConfig(request).configure(table)

    context = {
        'table': table,
        'title': 'List de proveedores'
    }

    return render(
        request,
        template_name='menu_estacionamiento/proveedores.html',
        context=context
    )


@login_required
def historial(request):
    return render(
        request,
        template_name='menu_estacionamiento/historial.html',
        context={}
    )
