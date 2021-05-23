import csv
from datetime import date, time, timedelta, datetime
import json
from threading import Thread
import os

from django.conf import settings
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q, Sum, Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

from django_tables2 import RequestConfig

from .models import (
    RegistroEstacionamiento, Proveedor,
    CicloCaja, CicloMensual, Persona, CicloAnual,
    Cobros, Estacionado, AperturaManual, TarifaEspecial,
    Horarios_Precio, Dia_Especial
)
from .forms import EstacionamientoForm, AperturaManualForm, ProveedorForm
from .tables import HistorialEstacionamientoTable


def postpone(function):
    def decorator(*args, **kwargs):
        t = Thread(target=function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()

    return decorator


@postpone
def socket_arduino(cantidad):
    base_dir = settings.BASE_DIR
    script_loc = os.path.join(base_dir, 'scripts/client.py')
    os.system(f'python3 {script_loc} abrir_tiempo {cantidad}')


@login_required
def apertura_Manual(request):
    form = AperturaManualForm(request.POST or None)
    if form.is_valid():
        form.save()

    if request.method == 'POST':
        return redirect('estacionamiento:historial')

    else:
        return render(request, 'estacionamiento/apertura_manual.html',
                      {'form': form, 'title': 'Apertura Manual'})


@csrf_exempt
@login_required
def cobrarEntrada(request, id):
    if request.method == 'GET':
        entradaCobrar = RegistroEstacionamiento.objects.get(id=id)
        today = datetime.date(datetime.now())
        dia_Especial = Dia_Especial.objects.filter(
            Q(dia_Especial=today)
        ).distinct()
        if dia_Especial:
            # Hoy es día Especial
            tarifaEspacial = TarifaEspecial.objects.all().last()
            return JsonResponse(tarifaEspacial.precio, safe=False)

        time = datetime.time(datetime.now())
        horarios = Horarios_Precio.objects.all()
        i = 0
        for horario in horarios:
            i = i + 1
            diference = max(time, horario.final)
            if time < horario.final or i == 3:
                tarifaNormal = horario.precio
                break

        return JsonResponse(tarifaNormal, safe=False)

    else:
        entradaCobrar = RegistroEstacionamiento.objects.get(id=id)
        today = datetime.date(datetime.now())
        dia_Especial = Dia_Especial.objects.filter(
            Q(dia_Especial=today)
        ).distinct()
        if dia_Especial:
            # Hoy es día Especial
            tarifaEspacial = TarifaEspecial.objects.all().last()
            cobro = Cobros(precio=tarifaEspacial.precio,
                           registroEstacionamiento=entradaCobrar, deuda=False)
            cobro.save()
            messages.warning(request, f'Cobro por ${tarifaEspacial}')
            # return redirect("estacionamiento:historial")
            return JsonResponse("Ok", safe=False)

        time = datetime.time(datetime.now())
        horarios = Horarios_Precio.objects.all()
        i = 0
        for horario in horarios:
            i = i + 1
            if time < horario.final or i == 3:
                tarifaNormal = horario.precio
                break

        cobro = Cobros(precio=tarifaNormal,
                       registroEstacionamiento=entradaCobrar, deuda=False)
        cobro.save()
        messages.warning(request, 'Cobro por $' + f'{tarifaNormal}')
        # return redirect("estacionamiento:historial")
        return JsonResponse("Ok", safe=False)


@csrf_exempt
@login_required
def pago_deuda(request, id):
    if request.method == "POST":
        entradaMoroso = RegistroEstacionamiento.objects.get(id=id)
        salida = str(entradaMoroso.persona.deuda)
        cobroDeuda = Cobros(precio=entradaMoroso.persona.deuda,
                            registroEstacionamiento=entradaMoroso, deuda=True)
        socioMoroso = entradaMoroso.persona
        socioMoroso.deuda = 0.0
        socioMoroso.general = True
        socioMoroso.save()
        cobroDeuda.save()
        entradaMoroso.tipo = 'SOCIO'
        entradaMoroso.autorizado = True
        entradaMoroso.save()
        messages.warning(request, 'Pago de deuda por $' + f'{salida}' ' dirigirse hacia administración para realizar el pago')
        return JsonResponse("Ok", safe=False)
    else:
        entradaMoroso = RegistroEstacionamiento.objects.get(id=id)
        salida = entradaMoroso.persona.deuda
        return JsonResponse(salida, safe = False)
    #return HttpResponse(salida)


@login_required
def emision_resumen_anterior(request, id):
    cicloCajaR = CicloCaja.objects.get(id=id)
    cicloMensualActual = CicloMensual.objects.all().last()
    if cicloMensualActual.cicloMensual == cicloCajaR.cicloMensual.cicloMensual:
        return redirect('menu_estacionamiento:menu_estacionamiento')

    else:
        resumen_mensual = RegistroEstacionamiento.objects.\
            values("persona__nombre_apellido", "persona__nrSocio").\
            annotate(cantidad_Entradas=Count("id")).\
            order_by("persona__nombre_apellido").\
            exclude(persona__isnull=True).\
            filter(direccion='SALIDA', cicloCaja__cicloMensual=cicloCajaR.cicloMensual.cicloMensual,
                   autorizado=True)

        output = []
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        output.append(['NrSocio', 'Persona', 'Cantidad_Entradas'])

        for entrada in resumen_mensual:
            output.append([entrada['persona__nrSocio'],
                           entrada['persona__nombre_apellido'],
                           entrada['cantidad_Entradas']])

        writer.writerows(output)
        response['Content-Disposition'] = \
            'attachment; filename="resumen_mensual_'\
            f'{cicloCajaR.cicloMensual.cicloMensual}_año_'\
            f'{cicloCajaR.cicloMensual.cicloAnual.cicloAnual}.csv"'
        return response


@login_required
def emision_resumen_mensual(request):  # Falta testing
    cicloCaja_ = CicloCaja.objects.all().last()
    if cicloCaja_.recaudado is not None:
        cicloMensual_ = CicloMensual.objects.all().last()
        resumen_mensual = RegistroEstacionamiento.objects.\
            values("persona__nombre_apellido", "persona__nrSocio").\
            annotate(cantidad_Entradas=Count("id")).\
            order_by("persona__nombre_apellido").\
            exclude(persona__isnull=True).\
            filter(direccion='SALIDA', cicloCaja__cicloMensual=cicloMensual_,
                   autorizado=True)

        output = []
        cicloMensual_.finalMes = now()
        cicloMensual_.save()
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        output.append(['NrSocio', 'Persona', 'Cantidad_Entradas'])

        for entrada in resumen_mensual:
            output.append([entrada['persona__nrSocio'],
                           entrada['persona__nombre_apellido'],
                           entrada['cantidad_Entradas']])

        writer.writerows(output)
        response['Content-Disposition'] = \
            'attachment; filename="resumen_mensual_'\
            f'{cicloMensual_.cicloMensual}_año_'\
            f'{cicloMensual_.cicloAnual.cicloAnual}.csv"'
        cicloAnual_ = CicloAnual.objects.all().last()

        if cicloMensual_.cicloMensual >= 12:
            cicloAnual_ = CicloAnual(cicloAnual=(cicloAnual_.cicloAnual + 1))
            cicloAnual_.save()
            cicloAnual_ = CicloAnual.objects.all().last()
            cicloMensual_ = CicloMensual(cicloMensual=1,
                                         cicloAnual=cicloAnual_, inicioMes=now())
            cicloMensual_.save()

        else:
            cicloMensual_ = CicloMensual(
                cicloMensual=(cicloMensual_.cicloMensual + 1),
                cicloAnual=cicloAnual_, inicioMes=now()
            )
            cicloMensual_.save()

        cicloMensual_ = CicloMensual.objects.all().last()
        cicloCaja_ = CicloCaja(cicloCaja=1, cicloMensual=cicloMensual_, inicioCaja=now())
        cicloCaja_.save()
        return response

    else:
        messages.warning(request, 'Error debe cerrar caja primero')
        return redirect('menu_estacionamiento:menu_estacionamiento')

@csrf_exempt
@login_required
def cierre_caja(request):
    if request.method == 'GET':
        cicloCaja_ = CicloCaja.objects.all().last()
        cobros = Cobros.objects.values("registroEstacionamiento__identificador", "precio").filter(registroEstacionamiento__cicloCaja=cicloCaja_, deuda=False).distinct()
        if not cobros:
            resp = {
                "dinero": '0.0',
                "cobros": ''
            }
            return JsonResponse(resp, safe=False)
        if cicloCaja_.recaudado:
            return JsonResponse("Caja ya cerrada",safe=False)
        cobrosDic = []
        for cobro in cobros:
            cobrosDic.append({"persona":cobro['registroEstacionamiento__identificador'],"precio":cobro['precio']})
        recaudado = Cobros.objects.filter(
            registroEstacionamiento__cicloCaja=cicloCaja_, deuda=False).\
            aggregate(recaudacion=Sum('precio'))
        if recaudado['recaudacion']:
            cicloCaja_.recaudado = recaudado['recaudacion']
        else:
            cicloCaja_.recaudado = 0.0
            recaudado['recaudacion'] = '0.0'

        dinero = recaudado['recaudacion']
        resp = {
            "dinero": dinero,
            "cobros": cobrosDic
        }
        return JsonResponse(resp, safe=False)
        #context ={'recaudado':dinero}
        #messages.warning(request, 'Lo recaudado en esta caja fue de $'+ f'{dinero}')
    else:
        cicloCaja_ = CicloCaja.objects.all().last()
        recaudado = Cobros.objects.filter(
            registroEstacionamiento__cicloCaja=cicloCaja_, deuda=False).\
            aggregate(recaudacion=Sum('precio'))
        if recaudado['recaudacion']:
            cicloCaja_.recaudado = recaudado['recaudacion']
            cicloCaja_.finalCaja = now()
            cicloCaja_.usuarioCaja = request.user
            cicloCaja_.save()

        else:
            cicloCaja_.recaudado = 0.0
            cicloCaja_.finalCaja = now()
            cicloCaja_.usuarioCaja = request.user
            cicloCaja_.save()

        messages.warning(request, 'Lo recaudado en esta caja fue de $'+ f'{cicloCaja_.recaudado}')
        return JsonResponse("Ok",safe=False)
    #return redirect('menu_estacionamiento:menu_estacionamiento')
    #return JsonResponse(dinero, safe=False)


def funcionCobros(dato):
    today = now()
    ayer = today - timedelta(days=1)
    cobro = Cobros.objects.filter(
        Q(registroEstacionamiento__noSocio=int(dato)) |
        Q(registroEstacionamiento__persona__nrTarjeta=int(dato)),
        Q(registroEstacionamiento__tiempo__range=(ayer, today)),
    ).distinct()
    if cobro:
        return False

    else:
        return tiempoTolerancia(dato)


def tiempoTolerancia(dato):
    today = now()
    tolerancia = today - timedelta(minutes=15)
    entrada = RegistroEstacionamiento.objects.filter(
        Q(tiempo__range=(tolerancia, today)),
        Q(noSocio=int(dato)),
        Q(direccion='ENTRADA')
    )

    if entrada:
        # No excedio tiempo tolerancia
        return False

    else:
        # Excedio tiempo tolerancia
        return True


def funcionEliminarEstacionado(entrada):
    try:
        estacionado = Estacionado.objects.all()
        estacionado.filter(
            registroEstacionamiento__identificador=entrada.identificador
        ).delete()
        return 0

    except:
        return 1


def respuesta(request):
    if request.method == 'GET':
        # El tipo de dato que vamos a recibir (NrTarjeta=0/DNI=1/Proveedor=2)
        tipo = request.GET.get('tipo', '')
        dato = request.GET.get('dato', '')
        direccion_ = request.GET.get('direccion', '')
        cicloCaja_ = CicloCaja.objects.all().last()
        if cicloCaja_.recaudado is not None:
            newCicloCaja = CicloCaja(cicloMensual=cicloCaja_.cicloMensual,
                                     cicloCaja=(cicloCaja_.cicloCaja + 1), inicioCaja=now())
            newCicloCaja.save()
            cicloCaja_ = CicloCaja.objects.all().last()

        if int(direccion_) == 1:
            direccion_ = 'SALIDA'
            if int(tipo) == 0:
                try:
                    user = Persona.objects.get(nrTarjeta=int(dato))
                    if user.general:
                        entrada = RegistroEstacionamiento(
                            tipo='SOCIO',
                            lugar='ESTACIONAMIENTO',
                            persona=user,
                            direccion=direccion_,
                            autorizado=tiempoTolerancia(dato),
                            cicloCaja=cicloCaja_
                        )
                        entrada.save()
                        # abrir barrera
                        messages.warning(request, 'Salida Socio Autorizada')
                        rta = '#1' #salida socio
                        funcionEliminarEstacionado(entrada)

                    else:
                        resultado = funcionCobros(dato)
                        if not resultado:
                            entrada = RegistroEstacionamiento(
                                tipo='SOCIO-MOROSO',
                                lugar='ESTACIONAMIENTO',
                                persona=user,
                                direccion=direccion_,
                                autorizado=False,
                                cicloCaja=cicloCaja_
                            )
                            entrada.save()
                            messages.warning(request, 'Salida Socio-Moroso Autorizada')
                            rta = '#1'   #salida sociomoroso autorizada
                            # Registro Socio Moroso Cobro por NoSocio
                            funcionEliminarEstacionado(entrada)
                        else:
                            messages.warning(request, 'Socio-Moroso no pago la Deuda o no Pago el Estacionamiento')
                            rta = '#6'  # SocioMoroso no pago Deuda o no Pago Entrada
                except:
                    messages.warning(request, 'La Tarjeta no Existe. Ingresar con DNI')
                    rta = '#2'  # El usuario No existe

            elif int(tipo) == 1:
                try:
                    user = Persona.objects.get(dni=int(dato))
                    if user.general:
                        entrada = RegistroEstacionamiento(
                            tipo='SOCIO',
                            lugar='ESTACIONAMIENTO',
                            persona=user,
                            direccion=direccion_,
                            autorizado=tiempoTolerancia(dato),
                            cicloCaja=cicloCaja_
                        )
                        entrada.save()
                        messages.warning(request, 'Salida Socio Autorizada por DNI')
                        rta = '#1' #salida socio autorizada por dni
                        funcionEliminarEstacionado(entrada)

                    else:
                        resultado = funcionCobros(dato)
                        if not resultado:
                            entrada = RegistroEstacionamiento(
                                tipo='SOCIO-MOROSO',
                                lugar='ESTACIONAMIENTO',
                                persona=user,
                                direccion=direccion_,
                                autorizado=False,
                                cicloCaja=cicloCaja_
                            )
                            entrada.save()
                            messages.warning(request, 'Salida Socio-Moroso Autorizada por DNI')
                            rta = '#1' #salida socio moroso autorizada  
                            # Registro Socio Moroso Cobro por NoSocio
                            funcionEliminarEstacionado(entrada)
                        else:
                            messages.warning(request, 'Salida Socio-Moroso No Autorizada Dirigirse a Portería')
                            rta = '#6'  # NoSocio no pago Deuda o no Pago Entrada

                except:
                    if not funcionCobros(dato):
                        entrada = RegistroEstacionamiento(
                            tipo='NOSOCIO',
                            lugar='ESTACIONAMIENTO',
                            noSocio=dato,
                            direccion=direccion_,
                            autorizado=True,
                            cicloCaja=cicloCaja_
                        )
                        entrada.save()
                        messages.warning(request, 'Salida NoSocio Autorizada')
                        rta = '#1' #salida no socio autorizada
                        funcionEliminarEstacionado(entrada)
                    else:
                        messages.warning(request, 'El No Socio no Pagó y Excedió Tiempo Tolerancia')
                        rta = '#5' #no puede salir
                        # El No Socio no pagó y excedió
                        # el tiempo de tolerancia

            else:
                try:
                    proveedor_ = Proveedor.objects.get(idProveedor=int(dato))
                    entrada = RegistroEstacionamiento(
                        tipo='PROVEEDOR',
                        lugar='ESTACIONAMIENTO',
                        proveedor=proveedor_,
                        direccion=direccion_,
                        autorizado=True,
                        cicloCaja=cicloCaja_
                    )
                    entrada.save()
                    # Abrir barrera
                    messages.warning(request, 'Salida Proveedor Autorizada')
                    rta = '#1' #salida proveedores autorizada
                    funcionEliminarEstacionado(entrada)

                except:
                    messages.warning(request, 'El Codigo que digitó es incorrecto')
                    rta = '#4'  # Error Proveedor no encontrado

        else:
            direccion_ = 'ENTRADA'
            if int(tipo) == 0:
                try:
                    user = Persona.objects.get(nrTarjeta=int(dato))
                    if user.general:
                        entrada = RegistroEstacionamiento(
                            tipo='SOCIO',
                            lugar='ESTACIONAMIENTO',
                            persona=user,
                            direccion=direccion_,
                            autorizado=True,
                            cicloCaja=cicloCaja_
                        )
                        entrada.save()
                        messages.warning(request, 'Entrada Socio Registrada')
                        # Abrir barrera
                        rta = '#1' #Registro Socio

                    else:
                        #entrada = RegistroEstacionamiento(
                        #    tipo='SOCIO-MOROSO',
                        #    lugar='ESTACIONAMIENTO',
                        #    persona=user,
                        #    direccion=direccion_,
                        #    autorizado=False,
                        #    cicloCaja=cicloCaja_
                        #)
                        #entrada.save()
                        messages.warning(request, 'Usted es Socio Moroso, debe Ingresar con su DNI')
                        rta = '#7'  # Registro Socio Moroso el usuario debe dirigirse a la cabina de portería

                except:
                    messages.warning(request, 'La tarjeta que ingresó es incorrecta. Ingrese DNI')
                    rta = '#2'  # El usuario No existe ingresar DNI

            elif int(tipo) == 1:
                try:
                    user = Persona.objects.get(dni=int(dato))
                    if user.general:
                        entrada = RegistroEstacionamiento(
                            tipo='SOCIO',
                            lugar='ESTACIONAMIENTO',
                            persona=user,
                            direccion=direccion_,
                            autorizado=True,
                            cicloCaja=cicloCaja_
                        )
                        entrada.save()
                        messages.warning(request, 'Entrada Registrada por DNI. Acercarse a Portería')
                        rta = '#3' #Registro Socio 

                    else:
                        entrada = RegistroEstacionamiento(
                            tipo='SOCIO-MOROSO',
                            lugar='ESTACIONAMIENTO',
                            persona=user,
                            direccion=direccion_,
                            autorizado=False,
                            cicloCaja=cicloCaja_
                        )
                        entrada.save()
                        # Abrir barrera
                        messages.warning(request, 'Entrada Registrada por DNI. Acercarse a Portería')
                        rta = '#3'  # Registro Socio Moroso el usuario debe dirigirse a la cabina de portería

                except:
                    entrada = RegistroEstacionamiento(
                        tipo='NOSOCIO',
                        lugar='ESTACIONAMIENTO',
                        noSocio=int(dato),
                        direccion=direccion_,
                        autorizado=True,
                        cicloCaja=cicloCaja_
                    )
                    entrada.save()
                    messages.warning(request, 'Entrada Registrada por DNI. Acercarse a Portería.')
                    rta = '#3'  # NoSocio registrado el usuarios debe dirigirse a la cabina de portería

            else:
                try:
                    proveedor_ = Proveedor.objects.get(idProveedor=int(dato))
                    entrada = RegistroEstacionamiento(
                        tipo='PROVEEDOR',
                        lugar='ESTACIONAMIENTO',
                        proveedor=proveedor_,
                        direccion=direccion_,
                        autorizado=True,
                        cicloCaja=cicloCaja_
                    )
                    entrada.save()
                    # Abrir barrera
                    messages.warning(request, 'Entrada Proveedor Registrada')
                    rta = '#1'  #Entrada autorizada

                except:
                    messages.warning(request, 'El Codigo que digitó es incorrecto')
                    rta = '#4'  # Error Proveedor no encontrado
            try:
                funcionEliminarEstacionado(entrada)
                estacionado = Estacionado(registroEstacionamiento=entrada)
                estacionado.save()
            except:
                pass

        return JsonResponse(rta,safe=False)


@login_required
def historial_estacionamiento(request):
    if request.method == 'GET':
        estacionamiento = RegistroEstacionamiento.objects.all()

        busqueda = request.GET.get('buscar')
        fecha = request.GET.get('fecha')
        tiempo = request.GET.get('tiempo')
        caja_input = request.GET.get('caja')
        mensual_input = request.GET.get('caja_mensual')

        ciclo_anual = list(CicloAnual.objects.all().values())
        ciclo_mensual = list(CicloMensual.objects.all().values())
        ciclo_caja = list(CicloCaja.objects.all().values())

        if busqueda:
            estacionamiento = estacionamiento.filter(
                Q(identificador__icontains=busqueda),
            ).distinct()

        if fecha:
            fecha = str(fecha).split('-')
            fecha = date(int(fecha[0]), int(fecha[1]), int(fecha[2]))
            estacionamiento = estacionamiento.filter(
                tiempo__date=fecha
            )

        if tiempo:
            tiempo = str(tiempo).split(':')
            tiempo = time(int(tiempo[0]), int(tiempo[1]))
            estacionamiento = estacionamiento.filter(
                tiempo__hour=tiempo.hour,
                tiempo__minute=tiempo.minute
            )

        if caja_input:
            estacionamiento = estacionamiento.filter(cicloCaja=caja_input)
            messages.info(request, f'Visualizando \
                          {CicloCaja.objects.get(id=caja_input)}')

        if mensual_input:
            estacionamiento = estacionamiento.filter(
                cicloCaja__cicloMensual=mensual_input
            )
            messages.info(request, f'Visualizando \
                          {CicloMensual.objects.get(id=mensual_input)}')

        table = HistorialEstacionamientoTable(estacionamiento)
        RequestConfig(request).configure(table)

        return render(
            request,
            'estacionamiento/historial.html',
            {'table': table, 'title': 'Historial',
             'anual': ciclo_anual, 'mensual': ciclo_mensual,
             'caja': ciclo_caja, 'viscaja': caja_input,
             'vismes': mensual_input}
        )


@login_required
def detalle_estacionamiento(request, id):
    datos = RegistroEstacionamiento.objects.get(id=id)
    cobro = Cobros.objects.filter(
        Q(registroEstacionamiento__id__icontains=id)
    ).distinct()
    if cobro:
        cobrado = 'True'

    else:
        cobrado = 'False'

    return render(request, 'estacionamiento/detalle_historial.html',
                  {'datos': datos, 'title': 'Detalle Historial',
                   'cobrado': cobrado})


@login_required
def editar_estacionamiento(request, id):
    obj = RegistroEstacionamiento.objects.get(id=id)
    form = EstacionamientoForm(request.POST or None, instance=obj)

    # Cargo el form y el objeto del registro para poder renderizar ciertos
    # datos en el html.
    context = {
        'form': form,
        'obj': obj,
        'title': 'Detalle historial'
    }

    if request.method == 'POST':
        if form.is_valid():
            # Recibo las variables de ID y DNI para asignar al proveedor o
            # socio en los respectivos casos.
            idProveedor = request.POST.get('idProveedor')
            dni = request.POST.get('noSocio')

            # Chequeo el tipo de entrada que se selecciono al hacer la edicion.
            if form.cleaned_data['tipo'] == 'NOSOCIO':
                # En caso de que el tipo seleccionado haya sido NOSOCIO me
                # aseguro de eliminar cualquier proveedor o persona previamente
                # asignada en el form para evitar conflictos.
                form.cleaned_data['persona'] = None
                form.cleaned_data['proveedor'] = None
                # Realizo lo mismo pero para el objeto en particular para
                # eliminar cualquier persona o proveedor previamente guardado.
                obj.persona = None
                obj.proveedor = None
                obj.save()

            elif (form.cleaned_data['tipo'] == 'SOCIO' or
                  form.cleaned_data['tipo'] == 'SOCIO-MOROSO'):
                # En caso de que el tipo seleccionado sea SOCIO o SOCIO-MOROSO
                # y no haya ninguna persona seleccionada en el form, es decir,
                # asegura que es un socio pero no especifica cual, lo
                # redirecciona a la misma pagina para reiniciar el formulario.
                if not form.cleaned_data['persona']:
                    messages.warning(request, 'El formulario no fue \
                                     completado correctamente')
                    return redirect('estacionamiento:editar', id)

                else:
                    # Utilizando el DNI ingresado y la persona asociada para
                    # guardar el DNI del socio en la DB.
                    per = Persona.objects.get(id=obj.persona.id)
                    if dni:
                        per.dni = dni
                        per.save()

                    # Por ultimo chequeo que si el tipo seleccionado fue socio
                    # pero el socio sigue teniendo deuda, que la entrada cambie
                    # por la fuerza a socio-moroso nuevamente y se asegure
                    # que el autorizado se mantenga en False.
                    if (not per.general and
                       form.cleaned_data['tipo'] == 'SOCIO'):
                        form.cleaned_data['tipo'] = 'SOCIO-MOROSO'
                        form.cleaned_data['autorizado'] = funcionCobros(dni)
                        messages.warning(request, 'El tipo de entrada fue \
                                         cambiada a SOCIO-MOROSO por tener \
                                         deuda')

                    if (per.general and
                       form.cleaned_data['tipo'] == 'SOCIO-MOROSO'):
                        form.cleaned_data['tipo'] = 'SOCIO'
                        form.cleaned_data['autorizado'] = True
                        messages.warning(request, 'El tipo de entrada fue \
                                         cambiada a SOCIO por no tener deuda')

                    if (not obj.tipo == 'SOCIO-MOROSO' and
                       form.cleaned_data['tipo'] == 'SOCIO-MOROSO'):
                        # Si el tipo original no era socio-moroso, y se lo
                        # cambio a socio-moroso, por default no debe estar
                        # autorizado.
                        form.cleaned_data['autorizado'] = funcionCobros(dni)

            elif form.cleaned_data['tipo'] == 'PROVEEDOR':
                # Idem anterior pero en el caso de que el tipo seleccionado sea
                # proveedor y no haya proveedor asociado en el form.
                if not form.cleaned_data['proveedor']:
                    messages.warning(request, 'El formulario no fue \
                                     completado correctamente')
                    return redirect('estacionamiento:editar', id)

                elif idProveedor:
                    # Utilizando las variables recibidas del form, chequeo que
                    # haya un ID ingresado y un proveedor asociado para guardar
                    # el correspondiente ID al proveedor en cuestion.
                    prov = Proveedor.objects.get(id=obj.proveedor.id)
                    prov.idProveedor = idProveedor
                    prov.save()

            obj.usuarioEditor = request.user
            obj.save()
            form.save()
            return redirect('estacionamiento:historial')

        else:
            # Si existe algun error en el formulario, reinicia la pagina con
            # un mensaje de advertencia.
            messages.warning(request, 'El formulario no fue completado \
                             correctamente')
            return render(request, 'estacionamiento/editar_historial.html',
                          context)

    else:
        return render(request, 'estacionamiento/editar_historial.html',
                      context)


# La unica funcion de este view es la de que el codigo de js pueda hacer un
# a estos datos para renderizarlos en tiempo real sin tener que hacer otro
# request.
def fetch_proveedores(request):
    # Dentro del GET recibe como datos:
    page = request.GET.get('page')  # La pagina que quiere visualizar.
    filter_string = request.GET.get('filter-string')  # El string de filtro.

    # Separa el string para filtrar en un list con cada palabra ingresada.
    parsed_filter = filter_string.split(' ')

    # Filtra todos los proveedores con el string recibido por nombre de
    # proveedor.
    for filter in parsed_filter:
        proveedores = Proveedor.objects.all().filter(
            Q(nombre_proveedor__icontains=filter_string)
        ).order_by('nombre_proveedor')

    # Realiza la paginacion de los datos con un maximo de 20 proveedores por
    # pagina y especifica la pagina que quiere visualizar.
    paginated = Paginator(list(proveedores.values()), 20)
    proveedores = paginated.page(page).object_list

    # Agrega al json de respuesta los datos para que el codigo de js sepa
    # si la pagina que esta visualizandose tiene pagina siguiente o anterior.
    proveedores.append({
        'has_previous': paginated.page(page).has_previous(),
        'has_next': paginated.page(page).has_next()
    })

    # Devuelve la respuesta en forma de json especificando el 'safe=False'
    # para evitar tener problemas de CORS.
    return JsonResponse(proveedores, safe=False)


@login_required
def add_proveedor(request):
    form = ProveedorForm(request.POST or None)

    if request.method == 'GET':
        context = {'form': form, 'title': 'Agregar un proveedor'}
        return render(request, 'estacionamiento/agregar_proveedor.html',
                      context)

    elif request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, f"El proveedor \
                    {form.cleaned_data['nombre_proveedor']} se ha \
                    guardado correctamente")

        return redirect('menu_estacionamiento:proveedores')


@login_required
def detalle_proveedor(request, id):
    proveedor = Proveedor.objects.get(id=id)
    context = {'obj': proveedor, 'title': 'Detalle proveedor'}
    return render(request, 'estacionamiento/detalle_proveedor.html', context)


@login_required
def editar_proveedor(request, id):
    obj = Proveedor.objects.get(id=id)
    form = ProveedorForm(request.POST or None, instance=obj)
    context = {
        'form': form,
        'id': obj.id,
        'title': 'Editar proveedor',
        'subtitle': 'Editar'
    }
    return render(request, 'estacionamiento/agregar_proveedor.html', context)


@csrf_exempt
def fetch_Events(request):
    if request.method == 'GET':
        eventos = Dia_Especial.objects.values("dia_Especial").all()
        listeventos = []
        for evento in eventos:
            date_splitted = evento['dia_Especial'].\
                strftime('%d/%m/%Y').split('/')
            if date_splitted[0][0] == '0':
                day = date_splitted[0][1]
            else:
                day = date_splitted[0]

            if date_splitted[1][0] == '0':
                month = date_splitted[1][1]

            else:
                month = date_splitted[1]

            year = date_splitted[2]
            final_date = f'{day}/{month}/{year}'
            diction = {'date': final_date}
            listeventos.append(diction)
        return JsonResponse(listeventos, safe=False)
    else:
        r = request.body
        data = json.loads(r.decode())
        fecha = datetime.strptime(data['fecha'], '%d/%m/%Y')
        fecha = fecha.strftime('%Y-%m-%d')
        fecha = datetime.strptime(fecha, '%Y-%m-%d')
        if data['accion'] == "add":
            evento = Dia_Especial(dia_Especial=fecha)
            evento.save()
        elif data['accion'] == 'delete':
            Dia_Especial.objects.filter(dia_Especial=fecha).delete()
        return JsonResponse('Ok', safe=False)
