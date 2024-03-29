import csv
import os
from threading import Thread

import pandas as pd
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django_tables2 import RequestConfig

from estacionamiento.models import RegistroEstacionamiento
from estacionamiento.views import funcion_cobros
from registroGeneral.models import EntradaGeneral
from registroGeneral.tables import HistorialTable

from .forms import PersonaForm
from .models import Deuda, Persona


def postpone(function):
    def decorator(*args, **kwargs):
        t = Thread(target=function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()

    return decorator


@login_required
def lista_usuarios(request):
    return render(request, "usuario/lista_usuarios.html", {"title": "Lista de socios"})


@login_required
def lista_proveedores(request):
    return render(
        request, "usuario/lista_proveedores.html", {"title": "Lista de proveedores"}
    )


@login_required
def editar_usuario(request, id):
    obj = Persona.objects.get(id=id)
    form = PersonaForm(request.POST or None, instance=obj)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            estacionamiento = RegistroEstacionamiento.objects.filter(
                Q(identificador=form.cleaned_data["dni"])
                | Q(noSocio=form.cleaned_data["dni"]),
                Q(direccion="ENTRADA"),
                Q(tipo="NOSOCIO"),
            ).last()

            if estacionamiento and funcion_cobros(estacionamiento.noSocio) != "SI":
                estacionamiento.persona = obj
                if obj.estacionamiento:
                    estacionamiento.tipo = "SOCIO"
                    message = " Se modificaron los datos del DNI del socio. El socio no tiene deuda y no debe abonar tarifa ni regularizar la deuda."
                    if message not in estacionamiento.mensaje:
                        estacionamiento.mensaje += message

                else:
                    estacionamiento.tipo = "SOCIO-MOROSO"
                    message = " Se modificaron los datos del DNI del socio. El socio tiene deuda y debe regularizarla o abonar la tarifa correspondiente."
                    if message not in estacionamiento.mensaje:
                        estacionamiento.mensaje += message

                estacionamiento.save()
                messages.info(request, "1 registro del estacionamiento fue modificado")

        messages.success(request, "Los datos fueron guardados con éxito")
        return redirect("usuario:lista")

    else:
        return render(
            request,
            "usuario/editar_usuario.html",
            {"form": form, "title": "Editar socio"},
        )


@login_required
def historial(request):
    if request.method == "GET":
        entradas = EntradaGeneral.objects.all()
        busqueda = request.GET.get("buscar")
        fecha_inicio = request.GET.get("fecha-inicio")
        fecha_final = request.GET.get("fecha-final")

        context = {"title": "Historial"}

        if busqueda:
            entradas = entradas.filter(
                Q(lugar__icontains=busqueda)
                | Q(tiempo__icontains=busqueda)
                | Q(persona__nombre_apellido__icontains=busqueda)
                | Q(persona__dni__icontains=busqueda)
            ).distinct()

        if fecha_inicio and fecha_final:
            entradas = entradas.filter(
                tiempo__date__range=(fecha_inicio, fecha_final)
            ).distinct()
            context["finicio"] = fecha_inicio
            context["ffinal"] = fecha_final

        table = HistorialTable(entradas)
        RequestConfig(request).configure(table)

        context["table"] = table

        return render(request, "usuario/historial.html", context)


@login_required
def cargar_db(request):
    media_root = settings.MEDIA_ROOT
    location = os.path.join(media_root, "saldos.csv")

    try:
        df = pd.read_csv(
            location,
            encoding="latin_1",
            on_bad_lines="skip",
            names=list("abcdefghijklmnopqrstuv"),
        )

    except:
        messages.warning(request, "Ha habido un error al leer el archivo")
        return redirect("draganddrop:upload")

    for column in list("bdghijklmnopqrstuv"):
        df.drop(str(column), inplace=True, axis=1)

    for ind in df.index:
        if not pd.isna(df["f"][ind]):
            df["e"][ind] = df["f"][ind]

    df.drop("f", inplace=True, axis=1)
    df = df.rename(columns={"a": "NrSocio", "c": "Socio", "e": "Deuda"})
    if df["NrSocio"][5] != "Composición de Saldos":
        messages.warning(request, "El archivo subido es incorrecto")
        return redirect("draganddrop:upload")

    for row in range(10):
        df = df.drop(row)

    df = df.dropna(thresh=2)
    df["Deuda"] = df["Deuda"].fillna(0)

    cargar_db_async(df)

    messages.success(request, "La carga de datos ha iniciado con éxito")
    return redirect("usuariosistema:home")


@postpone
def cargar_db_async(df):
    deudaMax = Deuda.objects.all().last().deuda
    listaUsuarios = []
    for ind in df.index:
        if float(str(df["Deuda"][ind]).replace(",", "")) > deudaMax:
            try:
                usuario = Persona.objects.get(nrSocio=int(df["NrSocio"][ind]))
                listaUsuarios.append(usuario.id)
                usuario.general = False
                usuario.deuda = float(str(df["Deuda"][ind]).replace(",", ""))
                usuario.save()

            except:
                partes_nombre = str(df["Socio"][ind]).strip().split(" ")
                name = ""
                for nombre in partes_nombre:
                    if nombre:
                        name += f"{nombre} "

                usuario = Persona(
                    nombre_apellido=name.strip(),
                    nrSocio=int(df["NrSocio"][ind]),
                    general=False,
                    deuda=float(str(df["Deuda"][ind]).replace(",", "")),
                )
                usuario.save()
                usuario = Persona.objects.get(nrSocio=int(df["NrSocio"][ind]))
                listaUsuarios.append(usuario.id)

        else:
            try:
                usuario = Persona.objects.get(nrSocio=int(df["NrSocio"][ind]))
                listaUsuarios.append(usuario.id)
                usuario.general = True
                usuario.deuda = float(str(df["Deuda"][ind]).replace(",", ""))
                usuario.save()

            except:
                partes_nombre = str(df["Socio"][ind]).strip().split(" ")
                name = ""
                for nombre in partes_nombre:
                    if nombre:
                        name += f"{nombre} "

                usuario = Persona(
                    nombre_apellido=name.strip(),
                    nrSocio=int(df["NrSocio"][ind]),
                    general=True,
                    deuda=float(str(df["Deuda"][ind]).replace(",", "")),
                )
                usuario.save()
                usuario = Persona.objects.get(nrSocio=int(df["NrSocio"][ind]))
                listaUsuarios.append(usuario.id)

    personas = Persona.objects.all()
    for persona in personas:
        if persona.id not in listaUsuarios:
            persona.general = False
            persona.save(no_existe=True)

    try:
        noSocio = personas.get(nombre_apellido="NOSOCIO")
        noSocio.general = True
        noSocio.save()

    except:
        noSocio = Persona(nrSocio=0, nombre_apellido="NOSOCIO", general=True, deuda=0.0)
        noSocio.save()

    deudaMax = Deuda.objects.all().last().deudaEstacionamiento
    listaUsuarios = []
    for ind in df.index:
        if float(str(df["Deuda"][ind]).replace(",", "")) > deudaMax:
            try:
                usuario = Persona.objects.get(nrSocio=int(df["NrSocio"][ind]))
                listaUsuarios.append(usuario.id)
                usuario.estacionamiento = False
                usuario.deuda = float(str(df["Deuda"][ind]).replace(",", ""))
                usuario.save()

            except:
                partes_nombre = str(df["Socio"][ind]).strip().split(" ")
                name = ""
                for nombre in partes_nombre:
                    if nombre:
                        name += f"{nombre} "

                usuario = Persona(
                    nombre_apellido=name.strip(),
                    nrSocio=int(df["NrSocio"][ind]),
                    estacionamiento=False,
                    deuda=float(str(df["Deuda"][ind]).replace(",", "")),
                )
                usuario.save()
                usuario = Persona.objects.get(nrSocio=int(df["NrSocio"][ind]))
                listaUsuarios.append(usuario.id)

        else:
            try:
                usuario = Persona.objects.get(nrSocio=int(df["NrSocio"][ind]))
                listaUsuarios.append(usuario.id)
                usuario.estacionamiento = True
                usuario.deuda = float(str(df["Deuda"][ind]).replace(",", ""))
                usuario.save()

            except:
                partes_nombre = str(df["Socio"][ind]).strip().split(" ")
                name = ""
                for nombre in partes_nombre:
                    if nombre:
                        name += f"{nombre} "

                usuario = Persona(
                    nombre_apellido=name.strip(),
                    nrSocio=int(df["NrSocio"][ind]),
                    estacionamiento=True,
                    deuda=float(str(df["Deuda"][ind]).replace(",", "")),
                )
                usuario.save()
                usuario = Persona.objects.get(nrSocio=int(df["NrSocio"][ind]))
                listaUsuarios.append(usuario.id)

    personas = Persona.objects.all()
    for persona in personas:
        if persona.id not in listaUsuarios:
            persona.estacionamiento = False
            persona.save(no_existe=True)

    connection.close()


# La unica funcion de este view es la de que el codigo de js pueda hacer un
# a estos datos para renderizarlos en tiempo real sin tener que hacer otro
# request.
def fetch_usuarios(request):
    # Dentro del GET recibe como datos:
    page = request.GET.get("page")  # La pagina que quiere visualizar.
    filter_string = request.GET.get("filter-string")  # El string de filtro.
    order_by = request.GET.get("order-by")

    # Separa el string para filtrar en un list con cada palabra ingresada.
    parsed_filter = filter_string.split(" ")

    personas = Persona.objects.all()
    # Filtra todos los socios con el string recibido por nombre de
    # socio.
    for filter in parsed_filter:
        personas = personas.filter(
            Q(nombre_apellido__icontains=filter)
            | Q(dni__icontains=filter)
            | Q(nrSocio__icontains=filter),
            ~Q(nombre_apellido="NOSOCIO"),
        ).order_by(order_by)

    # Realiza la paginacion de los datos con un maximo de 20 proveedores por
    # pagina y especifica la pagina que quiere visualizar.
    paginated = Paginator(list(personas.values()), 20)
    personas = paginated.page(page).object_list

    # Agrega al json de respuesta los datos para que el codigo de js sepa
    # si la pagina que esta visualizandose tiene pagina siguiente o anterior.
    personas.append(
        {
            "has_previous": paginated.page(page).has_previous(),
            "has_next": paginated.page(page).has_next(),
        }
    )

    # Devuelve la respuesta en forma de json especificando el 'safe=False'
    # para evitar tener problemas de CORS.
    return JsonResponse(personas, safe=False)


@login_required
def download_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="Socios.csv"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "Nombre y apellido",
            "DNI",
            "Nr. de tarjeta",
            "Nr. de socio",
            "Deuda",
        ]
    )

    personas = Persona.objects.all().order_by("nombre_apellido", "dni", "nrSocio")

    for persona in personas.values_list(
        "nombre_apellido",
        "dni",
        "nrTarjeta",
        "nrSocio",
        "deuda",
    ):
        persona_list = list(persona)
        writer.writerow(persona_list)

    return response
