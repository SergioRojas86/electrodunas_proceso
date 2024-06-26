import csv
import boto3
from io import StringIO, BytesIO
import pandas as pd
import holidays
import numpy as np

def read_csv_from_s3(bucket_name, file_name):
    s3 = boto3.client('s3')
    try:
        response = s3.get_object(Bucket=bucket_name, Key=file_name)
        return response['Body'].read().decode('utf-8')
    except s3.exceptions.NoSuchKey:
        return None

def merge_and_upload_csv_log_to_s3(log_file, bucket_name_log, files_to_execute, s3_client, logger_com):
    # Nombres de las columnas
    column_names = ["fecha_datos", "fecha_actualizacion", "fecha_ejecucion"]

    # Leer el archivo CSV existente desde S3
    existing_csv_data = read_csv_from_s3(bucket_name_log, log_file)
    
    # Escribir los datos fusionados en un archivo temporal
    temp_csv_file = StringIO()
    csv_writer = csv.writer(temp_csv_file)

    # Fusionar los datos existentes con los nuevos datos
    merged_data = []
    if existing_csv_data:
        merged_data = list(csv.reader(StringIO(existing_csv_data)))
        merged_data.extend(files_to_execute)
    else:
        # Escribir los nombres de las columnas
        csv_writer.writerow(column_names)
        merged_data = files_to_execute
        
    # Escribir los datos fusionados
    csv_writer.writerows(merged_data)

    # Subir el archivo temporal actualizado a S3
    s3 = boto3.client('s3')
    s3.put_object(Body=temp_csv_file.getvalue(), Bucket=bucket_name_log, Key=log_file)
    
    logger_com.info("Se actualizo el log csv con los archivos ejecutados")
    
def generar_descripcion(row):
    if row['is_outlier_if']:
        descripcion = ""
        if row['Active_energy'] < row['Media_Diaria']:
            descripcion += "Registro por debajo de la media. "
        else:
            descripcion += "Registro por encima de la media. "
        
        if row['Es_Domingo']:
            descripcion += "Ocurrió en domingo. "
        
        if row['Festivo']:
            descripcion += "Ocurrió en un día festivo. "
        
        return descripcion
    else:
        return np.nan  # Retorna NaN si is_outlier_if no es True

def write_descriptive_file(s3_client, cleaning_bucket, Data, Data_ajustado, all_predictions, result='result'):
    
    file_desc = f'{result}/datos_descriptivos.csv'
    
    merged_data = pd.merge(Data[['Fecha', 'Active_energy', 'Reactive_energy', 'Cliente', 'Sector_Economico', 'is_outlier_if']],
                       Data_ajustado[['Fecha', 'Cliente', 'Media_Diaria']],
                       on=['Fecha', 'Cliente'], how='left')
    
    ## agregamos si tiene festivos y domingos para la descripción
    co_holidays = holidays.Colombia()
    
    def es_festivo(fecha):
        return fecha in co_holidays

    merged_data['Festivo'] = merged_data['Fecha'].apply(es_festivo)

    merged_data['Es_Domingo'] = merged_data['Fecha'].dt.dayofweek == 6
    
    # Función que genera la descripción basada en las condiciones dadas
    merged_data['Descripcion'] = merged_data.apply(generar_descripcion, axis=1)
    
    merged_data = merged_data.drop(['Festivo', 'Es_Domingo'], axis=1)

    merged_data['Fecha'] = pd.to_datetime(merged_data['Fecha'])
    all_predictions['Fecha'] = pd.to_datetime(all_predictions['Fecha'])

    all_predictions.rename(columns={'Prediccion_Active_Energy': 'Active_energy'}, inplace=True)

    predicciones_df = all_predictions[['Cliente', 'Fecha', 'Active_energy']]
    combined_data = pd.concat([merged_data, predicciones_df], ignore_index=True)
    combined_data['Anio'] = combined_data['Fecha'].dt.year #agregamos año
    combined_data['is_outlier_if'] = combined_data['is_outlier_if'].fillna('predict') ## reemplazamos por predict
    combined_data['Reactive_energy'].fillna(0, inplace=True)
    
    csv_buffer = BytesIO()
    combined_data.to_csv(csv_buffer, index=False)
    s3_client.put_object(Bucket=cleaning_bucket, Key=file_desc, Body=csv_buffer.getvalue())
    
    
