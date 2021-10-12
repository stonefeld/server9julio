from datetime import datetime
import os
import json

from django.conf import settings
from django.utils.timezone import now

from estacionamiento.models import CicloAnual, CicloCaja, CicloMensual, HorariosPrecio, TarifaEspecial, TiempoTolerancia
from registroGeneral.models import EntradaGeneral
from usuario.models import Deuda, Persona


media_root = settings.MEDIA_ROOT
us_location = os.path.join(media_root, 'usuario.json')
rg_location = os.path.join(media_root, 'registroGeneral.json')

print('\nConfigurando deuda...')
deuda_general = 300
deuda_estacionamiento = 400
Deuda(deuda=deuda_general, deudaEstacionamiento=deuda_estacionamiento).save()
print('Deuda configurada\n')

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

print('Carga de datos finalizada\n')

print('Inicializando ciclos...')
anual = CicloAnual(cicloAnual=2021)
anual.save()
mensual = CicloMensual(cicloAnual=anual, cicloMensual=1, inicioMes=now())
mensual.save()
caja = CicloCaja(cicloMensual=mensual, cicloCaja=1, inicioCaja=now())
caja.save()

print('Inicializando precios por horarios...')
HorariosPrecio(precio=250, inicio='00:00:00', final='07:59:00').save()
HorariosPrecio(precio=300, inicio='08:00:00', final='15:59:00').save()
HorariosPrecio(precio=350, inicio='16:00:00', final='23:59:00').save()

print('Inicializando tarifa especial...')
TarifaEspecial(precio=500).save()

print('Inicializando tiempo de tolerancia...')
TiempoTolerancia(tiempo=15).save()

print('Inicializacion de variables finalizada')
