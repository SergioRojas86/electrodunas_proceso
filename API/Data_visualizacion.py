#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np
import re
#función que carga los datos para las visualizaciones y genera los datos separados para cada gráfico
def carga_datos(ruta):
    #se carga el archivo
    data = pd.read_csv(ruta,sep=',')
   
    return data

# ordenar los nombre de los clientes, considerando el número en el string
def obtener_numero(cliente):
    # Encuentra todos los números en el string, asumiendo que hay al menos uno
    numero = re.search(r'\d+', cliente)
    return int(numero.group()) if numero else 0

def filtro_data(data,filtro,filtro_anio):
    list_anios = list(data.Anio.unique())
    list_anios.insert(0,'TODOS')
    list_anios = {'anios':list_anios}
    list_clientes = {'clientes':[x for x in data.Cliente.unique()]}
    clientes_ordenados = sorted(list_clientes['clientes'], key=obtener_numero)
    clientes_ordenados.insert(0,'TODOS')
    list_clientes['clientes'] = clientes_ordenados
    total_clientes = len(data.Cliente.unique())
    
    #se generan los datos
    if filtro == 'TODOS' and filtro_anio == 'TODOS':       

        consumo_sector = data.groupby('Sector_Economico').agg(energia_activa = ('Active_energy','sum'),
                                                              energia_reactiva = ('Reactive_energy','sum')).reset_index()
        consumo_sector.columns = ['Sector','energia_activa','energia_reactiva']
        consumo_historico = data.groupby('Fecha').agg(energia_activa = ('Active_energy','sum'),
                                                              energia_reactiva = ('Reactive_energy','sum')).reset_index()
        consumo_historico.columns = ['fecha','energia_activa','energia_reactiva']
        consumo_historico['anomalo'] = ''
        consumo_filtrado = data[['Fecha','Cliente','Active_energy','Reactive_energy','is_outlier_if']]
        consumo_filtrado.columns = ['fecha','Cliente','energia_activa','energia_reactiva','anomalo']
        mean_act = str(round(consumo_historico.energia_activa.mean(),1))
        mean_rea = str(round(consumo_historico.energia_reactiva.mean(),1))
        min_act = str(round(consumo_historico.energia_activa.min(),1)) 
        min_rea = str(round(consumo_historico.energia_reactiva.min(),1)) 
        max_act = str(round(consumo_historico.energia_activa.max(),1)) 
        max_rea = str(round(consumo_historico.energia_reactiva.max(),1)) 
        des_est =  str(round(consumo_historico.energia_activa.std(),1))  
        lista = consumo_historico.energia_activa.tolist()
        tasa_cre = str(round((lista[-1]-lista[0])/lista[0] * 100,1)) + "%"
        total_anomali = int(float(len(data[data.is_outlier_if == True]))) 
        perc_anomali = str(int(round((len(data[data.is_outlier_if == True]) / len(data)) * 100,0))) + "%"
        

    else:        
        data2 = data.copy()
        if filtro != 'TODOS' and filtro_anio=='TODOS':
                data2 = data2[(data2.Cliente == filtro)]   
        elif filtro != 'TODOS' and filtro_anio!='TODOS': 
                filtro_anio = int(filtro_anio)               
                data2 = data2[(data2.Cliente == filtro) & (data2.Anio == filtro_anio)]           
        elif filtro == 'TODOS' and filtro_anio!='TODOS':
                filtro_anio = int(filtro_anio) 
                data2 = data2[(data2.Anio == filtro_anio)]        
        if len(data2)>0:
            total_clientes = len(data2.Cliente.unique())
            
            mean_act = str(round(data2.Active_energy.mean(),2))
            mean_rea =str(round(data2.Reactive_energy.mean(),2))
            min_act = str(round(data2.Active_energy.min(),2)) 
            min_rea = str(round(data2.Reactive_energy.min(),2)) 
            max_act = str(round(data2.Active_energy.max(),2)) 
            max_rea = str(round(data2.Reactive_energy.max(),2)) 
            consumo_sector = data2.groupby('Sector_Economico').agg(energia_activa = ('Active_energy','sum'),
                                                                energia_reactiva = ('Reactive_energy','sum')).reset_index()   
            consumo_sector.columns = ['Sector','energia_activa','energia_reactiva']
            consumo_historico = data2.groupby('Fecha').agg(energia_activa = ('Active_energy','sum'),
                                                                energia_reactiva = ('Reactive_energy','sum')).reset_index()
            consumo_historico.columns = ['fecha','energia_activa','energia_reactiva']
            consumo_historico['anomalo'] = ''
            consumo_filtrado = data2[['Fecha','Cliente','Active_energy','Reactive_energy','is_outlier_if']]
            consumo_filtrado.columns = ['fecha','Cliente','energia_activa','energia_reactiva','anomalo']
            des_est =  str(round(consumo_historico.energia_activa.std(),1))  
            lista = consumo_historico.energia_activa.tolist()
            tasa_cre = str(round((lista[-1]-lista[0])/lista[0] * 100,1)) + "%"
            total_anomali = int(len(data2[data2.is_outlier_if == True]))
            perc_anomali = str(int(round((len(data2[data2.is_outlier_if == True]) / len(data2)) * 100,0))) + "%"
        else:
            total_clientes = 'Sin data'
            mean_act = '0' 
            mean_rea ='0'
            min_act = '0'
            min_rea ='0'
            max_act = '0'
            max_rea = '0'
            des_est = '0'
            tasa_cre = '0%'
            perc_anomali = '0%'

            consumo_sector = data2.groupby('Sector_Economico').agg(energia_activa = ('Active_energy','sum'),
                                                                energia_reactiva = ('Reactive_energy','sum')).reset_index()   
            consumo_sector.columns = ['Sector','energia_activa','energia_reactiva']
            consumo_sector.loc[0] = ['0','0','0']
            consumo_historico = data2.groupby('Fecha').agg(energia_activa = ('Active_energy','sum'),
                                                                energia_reactiva = ('Reactive_energy','sum')).reset_index()
            consumo_historico.columns = ['fecha','energia_activa','energia_reactiva']
            consumo_historico['anomalo'] = ''
            consumo_historico.loc[0] = ['0','0','0',False]
            consumo_filtrado = data2[['Fecha','Cliente','Active_energy','Reactive_energy','is_outlier_if']]
            consumo_filtrado.columns = ['fecha','Cliente','energia_activa','energia_reactiva','anomalo']
            consumo_filtrado.loc[0] = ['0','0','0','0',False]
            total_anomali = 0
         
            
    total_anomali = "{:,.0f}".format(total_anomali)
    return list_anios,list_clientes, total_clientes, des_est,tasa_cre,mean_act, mean_rea, min_act, min_rea,max_act,max_rea,total_anomali,perc_anomali,consumo_sector,consumo_historico,consumo_filtrado

def anom_cliente(data,filtro,filtro_anio):
    if filtro == 'TODOS' and filtro_anio == 'TODOS':  
        df = data[data.is_outlier_if == 'True']
        df = df[['Cliente','Fecha','Descripcion','Sector_Economico','Active_energy']]
       

    else:
        if filtro != 'TODOS' and filtro_anio=='TODOS':
                df = data[(data.Cliente == filtro) & (data.is_outlier_if == 'True')] 
        elif filtro != 'TODOS' and filtro_anio!='TODOS':
                filtro_anio = int(filtro_anio) 
                df = data[(data.Cliente == filtro) & (data.is_outlier_if == 'True') & (data.Anio == filtro_anio)]  
        elif filtro == 'TODOS' and filtro_anio!='TODOS':
                filtro_anio = int(filtro_anio) 
                df = data[(data.is_outlier_if == 'True') & (data.Anio == filtro_anio)] 
        
        df = df[['Cliente','Fecha','Descripcion','Sector_Economico','Active_energy']]
    return df

