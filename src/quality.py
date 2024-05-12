import boto3
import pandas as pd
from io import BytesIO

def check_csv_columns(s3_client, bucket, key, required_columns):
    response = s3_client.get_object(Bucket=bucket, Key=key)
    data = response['Body'].read()
    df = pd.read_csv(BytesIO(data))
    return all(column in df.columns for column in required_columns)

def columns_to_use(s3_client, files_to_execute, cleaning_bucket, clean_folder):
    
    # Columnas requeridas
    csv_columns = ['Active_energy', 'Reactive_energy', 'Voltaje_FA', 'Voltaje_FC']
    xlsx_columns = ['Cliente:', 'Sector Económico:']
    
    files_to_check = [f"{clean_folder}/{item[0]}/" for item in files_to_execute]
    
    response = s3_client.list_objects_v2(Bucket=cleaning_bucket, Prefix=clean_folder)
    
    if 'Contents' in response:
        for obj in response['Contents']:
            key = obj['Key']
            # Verificar si el archivo está en uno de los directorios especificados
            if any(key.startswith(directory) for directory in files_to_check):
                if key.endswith('.csv'):
                    if check_csv_columns(s3_client, cleaning_bucket, key, csv_columns):
                        print(f"{key}: Contiene todas las columnas requeridas.")  
                    else:
                        print(f"{key}: NO contiene todas las columnas requeridas.")