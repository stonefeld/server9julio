from .models import Persona, Entrada
import pandas as pd

def cargarDB():
    deudaMax = 300
    listaUsuarios = [] #lista de usuarios actualizados
    location = '../media/saldos.csv'
    #xlsx = pd.ExcelFile('C:/Users/User/Desktop/Servidor SAGVB/saldos.xls')
    try:
        df = pd.read_csv(location,encoding='unicode_escape',error_bad_lines=False, names = list('abcdefghijklmnopqrstuv'))#name=list('abecedario')
    except :
        pass #terminar el programa
    df.drop('b', inplace=True, axis=1)
    df.drop('d', inplace=True, axis=1)
    for column in list('ghijklmnopqrstuv'):
        df.drop('%c'% (column), inplace=True, axis=1)
    for ind in df.index:
        if pd.isna(df['f'][ind]) == False:
            df['e'][ind] = df['f'][ind]
    df.drop('f', inplace=True, axis=1)
    df = df.rename(columns={'a':'NrSocio', 'c':'Socio','e':'Deuda'})
    if df['NrSocio'][6] != 'Composición de Saldos':
        pass #terminar el programa saltar error 
    for row in range(10):
        df = df.drop(row)
    df = df.dropna()
    for ind in df.index :
        if float((df['Deuda'][ind]).replace(',',''))>deudaMax:#si deuda es mayor a deudaMax .replace(',','')
            try:
                usuario = Persona.objects.get(nrSocio = int(df['NrSocio'][ind])) #cambiar la entrada a false
                listaUsuarios.append(usuario.id)
                if usuario.general == True: #cambiar entrada solo si es necesario cambiarlo
                    usuario.general = False
                    usuario.deuda = float((df['Deuda'][ind]).replace(',',''))
                    usuario.save()
            except:
                usuario = Persona(nombre = df['Socio'][ind], nrSocio = int(df['NrSocio'][ind]), general = False, deuda = float((df['Deuda'][ind]).replace(',','')) ) #sino existe el usuario crearlo
                usuario.save()
                usuario = Persona.objects.get(nrSocio = int(df['NrSocio'][ind]))
                listaUsuarios.append(usuario.id)
        else: #sino 
            try:
                usuario = Persona.objects.get(nrSocio = int(df['NrSocio'][ind])) #cambiar entrada a true
                listaUsuarios.append(usuario.id)
                if usuario.general == False:#cambiar entrada solo si es necesario cambiarlo
                    usuario.general = True
                    usuario.deuda = float((df['Deuda'][ind]).replace(',',''))
                    usuario.save()
            except :
                usuario = Persona(nombre = df['Socio'][ind], nrSocio = int(df['NrSocio'][ind]), general = True, deuda = float((df['Deuda'][ind]).replace(',','')) ) #sino existe el usuario crearlo
                usuario.save()
                usuario = Persona.objects.get(nrSocio = int(df['NrSocio'][ind]))
                listaUsuarios.append(usuario.id)

    personas = Persona.objects.all()
    for persona in personas:
        if persona.id not in listaUsuarios:
            persona.general = False
            persona.save()
