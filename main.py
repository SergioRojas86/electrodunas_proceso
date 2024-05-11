import sys
import json
from src.utils.logger_config import configure_logger, upload_log_to_s3
from src.utils.write_csv import merge_and_upload_csv_to_s3
import boto3 
import datetime

# Configura el logger
current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
log_file_name = f'ejecución_{current_date}.log'
logger = configure_logger(log_file_name)

def main(log_file, bucket_name_log, files_to_execute, s3_client):
    
    # Se ejecuta el proceso que actualiza o crea el archivo las fechas que han sido ejecutadas  
    merge_and_upload_csv_to_s3(log_file, bucket_name_log, files_to_execute, s3_client, logger)
    
    
    
if __name__ == "__main__":
    s3_client = boto3.client('s3')
    #bucket_name_log = 'electrodunas-log-files'
    #log_file = "log_executed_files.csv"
    
    json_arg = sys.argv[1]
    data = json.loads(json_arg)
    log_bucket = data['log_bucket']
    log_file = data['log_file']
    cleaning_bucket = data['cleaning_bucket']
    clean_folder = data['clean_folder']
    stage_folder = data['stage_folder']
    files_to_execute = data['files_to_execute']
    
    logger.info(f'Parametros de ejecución: log_bucket: {log_bucket} - log_file: {log_file} - cleaning_bucket: {cleaning_bucket} - clean_folder: {clean_folder} - stage_folder: {stage_folder}')
    
    if files_to_execute:
        logger.info(f'Se realizara el procesamiento de las fechas: {files_to_execute}')
        main(log_file, log_bucket, files_to_execute, s3_client)
        upload_log_to_s3(log_file_name, log_bucket, s3_client, logger)
    else:
        logger.info(f'No hay fechas para procesar')
        upload_log_to_s3(log_file_name, log_bucket, s3_client, logger)
    