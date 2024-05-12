import boto3
import pandas as pd
from io import BytesIO

# Función para verificar columnas en CSV
def check_csv_columns(s3_client, bucket, key, required_columns):
    response = s3_client.get_object(Bucket=bucket, Key=key)
    data = response['Body'].read()
    df = pd.read_csv(BytesIO(data))
    return all(column in df.columns for column in required_columns)

# Función para verificar columnas en XLSX
def check_xlsx_columns(s3_client, bucket, key, required_columns):
    response = s3_client.get_object(Bucket=bucket, Key=key)
    data = response['Body'].read()
    df = pd.read_excel(BytesIO(data), engine='openpyxl')
    return all(column in df.columns for column in required_columns)

def columns_to_use(s3_client, files_to_execute, cleaning_bucket, clean_folder):
    
    # Columnas requeridas
    csv_columns = ['Active_energy', 'Reactive_energy', 'Voltaje_FA', 'Voltaje_FC']
    xlsx_columns = ['Cliente:', 'Sector Económico:']
    
    files_to_check = [f"{clean_folder}/{item[0]}/" for item in files_to_execute]
    
    response = s3_client.list_objects_v2(Bucket=cleaning_bucket, Prefix=clean_folder)
    
    files_with_missing_columns=[]
    wrong_xlsx = 0
    
    if 'Contents' in response:
        for obj in response['Contents']:
            key = obj['Key']
            # Verificar si el archivo está en uno de los directorios especificados
            if any(key.startswith(directory) for directory in files_to_check):
                if key.endswith('.csv'):
                    if not check_csv_columns(s3_client, cleaning_bucket, key, csv_columns):
                        files_with_missing_columns.append(key)
                elif key.endswith('.xlsx'):
                    if not check_xlsx_columns(s3_client, cleaning_bucket, key, xlsx_columns):
                        wrong_xlsx = 1
                        
    if files_with_missing_columns:
        print('en la mala')
    if wrong_xlsx == 1:
        print('en la mala el catalogo')