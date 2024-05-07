import csv
import boto3
from io import StringIO

def read_csv_from_s3(bucket_name, file_name):
    s3 = boto3.client('s3')
    try:
        response = s3.get_object(Bucket=bucket_name, Key=file_name)
        return response['Body'].read().decode('utf-8')
    except s3.exceptions.NoSuchKey:
        return None

def merge_and_upload_csv_to_s3(log_file, bucket_name_log, files_to_execute, s3_client, logger_com):
    # Nombres de las columnas
    column_names = ["fecha_datos", "fecha_actualizacion", "fecha_ejecucion"]

    # Leer el archivo CSV existente desde S3
    existing_csv_data = read_csv_from_s3(bucket_name_log, log_file)

    # Fusionar los datos existentes con los nuevos datos
    merged_data = []
    if existing_csv_data:
        merged_data = list(csv.reader(StringIO(existing_csv_data)))

    merged_data.extend(files_to_execute)

    # Escribir los datos fusionados en un archivo temporal
    temp_csv_file = StringIO()
    csv_writer = csv.writer(temp_csv_file)
    
    # Escribir los nombres de las columnas
    csv_writer.writerow(column_names)
    
    # Escribir los datos fusionados
    csv_writer.writerows(merged_data)

    # Subir el archivo temporal actualizado a S3
    s3 = boto3.client('s3')
    s3.put_object(Body=temp_csv_file.getvalue(), Bucket=bucket_name_log, Key=log_file)
    
    logger_com.info("Se actualizo el log csv con los archivos ejecutados")
    print("Se actualizo el log csv con los archivos ejecutados")
