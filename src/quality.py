import boto3
import pandas as pd
from io import BytesIO

# verificar completitud
def completeness_csv(s3_client, logger, bucket, key):
    # completitud
    result = {}
    columns_with_low_completeness = {}
    response = s3_client.get_object(Bucket=bucket, Key=key)
    data = response['Body'].read()
    df = pd.read_csv(BytesIO(data))
    
    for column in list(df.columns):
        # valores nulos o vacios
        missing_values  = df[(df[column].isna())|(df[column].isnull())|(df[column]=="")]
        missing_count = len(missing_values)
        percentage = round((1-(missing_count/len(df)))*100,2)
        
        if percentage < 70:
            columns_with_low_completeness[column] = f"{percentage}%"
    if columns_with_low_completeness:
        result[key] = columns_with_low_completeness
        logger.info('WARNING: Archivos con una importante cantidad de data incompleta {result}')

# Función para verificar columnas en CSV
def check_csv_columns(s3_client, bucket, key, required_columns):
    response = s3_client.get_object(Bucket=bucket, Key=key)
    data = response['Body'].read()
    df = pd.read_csv(BytesIO(data))
    
    if key == '2021_Cliente_1.csv':
        print(df)
    return all(column in df.columns for column in required_columns)

# Función para verificar columnas en XLSX
def check_xlsx_columns(s3_client, logger, bucket, key, required_columns):
    response = s3_client.get_object(Bucket=bucket, Key=key)
    data = response['Body'].read()
    df = pd.read_excel(BytesIO(data), engine='openpyxl')
    
    missing_values_xlsx = df.isnull().any()
    if not missing_values_xlsx:
        logger.info('WARNING: El catalogo esta incompleto, este debe ser completado para que la data sea veridica')
    
    return all(column in df.columns for column in required_columns)

# revisra estructura y completitud de los archivos
def columns_to_use(s3_client, logger, files_to_execute, cleaning_bucket, clean_folder):
    
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
            print(response['Contents'])
            # verificar completitud
            completeness_csv(s3_client, logger, cleaning_bucket, key)
            # verificar estructura de los archivos, que contengan las columnas requeridas
            if any(key.startswith(directory) for directory in files_to_check):
                if key.endswith('.csv'):
                    if not check_csv_columns(s3_client, cleaning_bucket, key, csv_columns):
                        files_with_missing_columns.append(key)
                elif key.endswith('.xlsx'):
                    if not check_xlsx_columns(s3_client, logger, cleaning_bucket, key, xlsx_columns):
                        wrong_xlsx = 1
                        
    return files_with_missing_columns, wrong_xlsx
        
        
    