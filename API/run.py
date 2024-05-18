from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
from Data_visualizacion import carga_datos
from Data_visualizacion import filtro_data
from Data_visualizacion import anom_cliente
from collections import Counter
import json  # Importa el módulo json
import pandas as pd
#from modelo import load_model
#from modelo import make_prediction


#cargue de los datos iniciales
#data_kpi = carga_datos('data/Data_final.csv')

import boto3
from io import BytesIO

def carga_datos_s3(bucket_name, file_key):
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    data = pd.read_csv(BytesIO(obj['Body'].read()), low_memory=False)
    return data

# Carga inicial de datos desde S3
data_kpi = carga_datos_s3('electrodunas-clean-data', 'result/datos_descriptivos.csv')

list_anios, list_clientes, total_clientes,des_est,tasa_cre ,mean_act, mean_rea, min_act, min_rea,max_act,max_rea,total_anomali,perc_anomali,consumo_sector,consumo_historico,consumo_filtrado = filtro_data(data_kpi,'TODOS','TODOS')

print(tasa_cre)
#lanzamento de la api
app = Flask(__name__)

@app.route('/')
def index():

    cliente_seleccionado = request.args.get('cliente_seleccionado', default='TODOS')
    anio_seleccionado = request.args.get('anio_seleccionado', default='TODOS')
    return render_template('index.html', list_anios = list_anios,list_clientes=list_clientes, total_clientes=total_clientes,
                           des_est=des_est,tasa_cre=tasa_cre ,mean_act=mean_act,
                           mean_rea = mean_rea, min_act = min_act, min_rea = min_rea, max_act = max_act,max_rea = max_rea,
                           total_anomali = total_anomali, perc_anomali = perc_anomali,
                           cliente_seleccionado=cliente_seleccionado,anio_seleccionado=anio_seleccionado)

# grafico sector energia activa
@app.route('/get-sector-data')
def get_sector_data():
    anio_select = request.args.get('year', default='TODOS')  # Obtener el cliente desde los parámetros de la URL
    
    # Asegurarse de que 'consumo_sector' es un DataFrame válido y que contiene las columnas esperadas
    _, _, _, _,_,_, _, _, _,_,_,_,_,consumo_sector,_,_ = filtro_data(data_kpi,'TODOS',anio_select)

    sector_activa = consumo_sector[['Sector', 'energia_activa']].to_json(orient='records')
    return jsonify(json.loads(sector_activa))  # Usa json.loads para asegurar que se esté enviando como un array JSON

# grafico sector energia reactiva
@app.route('/get-sector-data_2')
def get_sector_data_2():
    anio_select = request.args.get('year', default='TODOS')  # Obtener el cliente desde los parámetros de la URL
    
    # Asegurarse de que 'consumo_sector' es un DataFrame válido y que contiene las columnas esperadas
    _, _, _, _,_,_, _, _, _,_,_,_,_,consumo_sector,_,_ = filtro_data(data_kpi,'TODOS',anio_select)
    # Asegurarse de que 'consumo_sector' es un DataFrame válido y que contiene las columnas esperadas
    sector_reactiva = consumo_sector[['Sector', 'energia_reactiva']].to_json(orient='records')

    return jsonify(json.loads(sector_reactiva))  # Usa json.loads para asegurar que se esté enviando como un array JSON

# gráfico serie de tiempo energía activa
@app.route('/get-time-series-data')
def get_time_series_data():
    client_name = request.args.get('client_id', default='TODOS')  # Obtener el cliente desde los parámetros de la URL
    anio_select = request.args.get('year', default='TODOS')  # Obtener el cliente desde los parámetros de la URL

    # Filtrar el dataframe basado en client_id, asumiendo que `df` es tu DataFrame
    _,_, _, _,_,_ ,_, _,_,_,_,_,_,_,consumo_historico,consumo_filtrado = filtro_data(data_kpi,client_name,anio_select)
    filtered_data = consumo_filtrado if client_name != 'TODOS' else consumo_historico

    # Encontrar el valor máximo y su fecha
    if len(filtered_data) == 1 :

       max_date = 0
 
       max_value = 0
    else:
       max_row = filtered_data.loc[filtered_data['energia_activa'].idxmax()]
       max_date = max_row['fecha']
       max_value = max_row['energia_activa']
       max_value = round(max_row['energia_activa'],1) if max_row['energia_activa']>1 else round(max_row['energia_activa'],2)

    #print(filtered_data)
    # Convertir los datos filtrados a JSON, incluyendo el valor máximo
    activa_time = filtered_data[['fecha', 'energia_activa','anomalo']].to_dict(orient='records')
    response_data = {
        'data': activa_time,
        'max_date': max_date,
        'max_value': max_value
    }
    
    response = Response(response_data)
    response.headers['Content-Length'] = len(response_data)
    return response

    return jsonify(response_data)

# gráfico serie de tiempo energía reactiva
@app.route('/get-time-series-data_2')
def get_time_series_data_2():
    client_name = request.args.get('client_id', default='TODOS')  # Obtener el cliente desde los parámetros de la URL
    anio_select = request.args.get('year', default='TODOS')  # Obtener el cliente desde los parámetros de la URL

    # Filtrar el dataframe basado en client_id, asumiendo que `df` es tu DataFrame
    _,_, _,_,_, _, _, _,_, _,_,_,_,_,consumo_historico,consumo_filtrado = filtro_data(data_kpi,client_name,anio_select)

    filtered_data = consumo_filtrado if client_name != 'TODOS' else consumo_historico
    
    # Encontrar el valor máximo y su fecha
    if len(filtered_data) == 1:
       max_date = 0
       max_value = 0
    else:
       max_row = filtered_data.loc[filtered_data['energia_reactiva'].idxmax()]
       max_date = max_row['fecha']
       max_value = max_row['energia_reactiva']
       max_value = round(max_row['energia_reactiva'],1) if max_row['energia_reactiva']>1 else round(max_row['energia_reactiva'],2)

    # Convertir los datos filtrados a JSON, incluyendo el valor máximo
    reactiva_time = filtered_data[['fecha', 'energia_reactiva','anomalo']].to_dict(orient='records')
   
    response_data = {
        'data': reactiva_time,
        'max_date': max_date,
        'max_value': max_value
    }

    return jsonify(response_data)


# Función para filtrar datos badados en la selección de un solo cliente
@app.route('/get-client-data', methods=['POST'])
def get_client_data():    
    client_name = request.json['client_name'] #recuperación de la variable cliente    
    anioselect = request.json['anioselect'] #recuperación de la variable cliente 
    
    # filtra de acuerdo al select de cliente
    list_anios,list_clientes, total_clientes, des_est,tasa_cre,mean_act, mean_rea, min_act, min_rea,max_act,max_rea,total_anomali,perc_anomali,consumo_sector,_,_ = filtro_data(data_kpi,client_name,anioselect)
    return jsonify({'total_clientes': total_clientes,'des_est':des_est,'tasa_cre':tasa_cre,'mean_act': mean_act, 'mean_rea' : mean_rea, 'min_act' : min_act, 'min_rea' : min_rea,
                    'max_act' : max_act,'max_rea' : max_rea,'total_anomali':total_anomali,'perc_anomali': perc_anomali})


## definiciones para la page novedades
@app.route('/novedades')
def novedades():
    cliente = request.args.get('cliente', default='TODOS')  
    anioselect = request.args.get('year', default='TODOS') #variable cliente para poder filtrar la tabla
    anomalias = data_kpi[data_kpi['is_outlier_if'] == True]
    conteo_por_sector = Counter(anomalias['Sector_Economico'])
    total_anomalias = len(anomalias)
    # Calcular porcentajes
    data_anomalias = [{'Sector': sector, 'Porcentaje': int(round((count / total_anomalias) * 100,0))} for sector, count in conteo_por_sector.items()]

    return render_template('novedades.html',data_anomalias=data_anomalias,list_anios=list_anios,list_clientes=list_clientes,cliente_seleccionado=cliente, anio_seleccionado =anioselect )

#api para controlar la informaci´n que se le entrega a novedades
@app.route('/api/anomalias')
def api_anomalias():
    #control de paginación para no cargar todos los registros al tiempo, sino hacer un cargue por lotes
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)  #cantidad de registros por página
    cliente = request.args.get('cliente', default='TODOS') #variable cliente para poder filtrar la tabla
    anioselect = request.args.get('year', default='TODOS') #variable cliente para poder filtrar la tabla
    tabla = anom_cliente(data_kpi, cliente,anioselect) #extracción de los datos necesarios para la tabla y para la gráfica
    total = len(tabla)
    start = (page - 1) * per_page
    end = start + per_page

    return jsonify({
        'data': tabla.iloc[start:end].to_dict(orient='records'),
        'total': total,
        'page': page,
        'pages': (total + per_page - 1) // per_page
    })
    

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8001)
    