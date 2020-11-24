import pandas as pd
from datetime import date

deudaMax = 300
listaUsuarios = [] #lista de usuarios actualizados
location = 'C:/Users/User/Desktop/Servidor SAGVB/saldosPrueba.csv'
today = date.today()
print(today.strftime("%Y%m%d"))

#xlsx = pd.ExcelFile('C:/Users/User/Desktop/Servidor SAGVB/saldos.xls')
df = pd.read_csv(location,encoding='unicode_escape',error_bad_lines=False, names = list('abcdefghijklmnopqrstuv'))#name=list('abecedario')
df.drop('b', inplace=True, axis=1)
df.drop('d', inplace=True, axis=1)
for column in list('ghijklmnopqrstuv'):
    df.drop('%c'% (column), inplace=True, axis=1)

for ind in df.index:
    if pd.isna(df['f'][ind]) == False:
        df['e'][ind] = df['f'][ind]

df.drop('f', inplace=True, axis=1)
df = df.rename(columns={'a':'NrSocio', 'c':'Socio','e':'Deuda'})
for row in range(10):
    df = df.drop(row)

df=df.dropna()
print(df)
