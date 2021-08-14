from datetime import datetime
import os
import json

from django.conf import settings
from django.db import connection, models

from registroGeneral.models import EntradaGeneral
from usuario.models import Persona, Deuda


media_root = settings.MEDIA_ROOT
us_location = os.path.join(media_root, 'usuario.json')
rg_location = os.path.join(media_root, 'registroGeneral.json')

deuda_general = 300
deuda_estacionamiento = 400
Deuda(deuda=deuda_general, deudaEstacionamiento=deuda_estacionamiento).save()

borrable = False

print('Cargando usuarios...')
with open(us_location) as f:
    usuarios = json.load(f)

for i, u in enumerate(list(usuarios), start=1):
    if u['model'] != 'usuario.deuda':
        dif = int(u['pk']) - i
        for o in range(dif):
            p = Persona(nombre_apellido='xX_borrar_despues_69_tula_Xx').save()
            borrable = True

        Persona(
            nombre_apellido=u['fields']['nombre_apellido'],
            dni=u['fields']['dni'],
            nrTarjeta=u['fields']['nrTarjeta'],
            nrSocio=u['fields']['nrSocio'],
            general=True if u['fields']['deuda'] < deuda_general else False,
            estacionamiento=True if u['fields']['deuda'] < deuda_estacionamiento else False,
            tenis=False,
            deuda=u['fields']['deuda'] if u['fields']['deuda'] is not None else 0,
        ).save()

if borrable:
    Persona.objects.get(nombre_apellido='xX_borrar_despues_69_tula_Xx').delete()

print('Cargando registros de entradas por molinete...')
with open(rg_location) as f:
    registros = json.load(f)

for r in list(registros):
    p = Persona.objects.get(id=r['fields']['persona'])
    fecha = r['fields']['tiempo'].split('T')[0].split('-')
    hora = r['fields']['tiempo'].split('T')[1].split(':')
    tiempo = datetime(year=int(fecha[0]), month=int(fecha[1]), day=int(fecha[2]), hour=int(hora[0]), minute=int(hora[1]), second=int(hora[2].split('.')[0]), microsecond=int(hora[2].split('.')[1].split('Z')[0]))
    EntradaGeneral(
        persona=p,
        lugar=r['fields']['lugar'],
        tiempo=tiempo,
        direccion=r['fields']['direccion'],
        autorizado=r['fields']['autorizado']
    ).save()

print('Carga de datos finalizada')
