import sys
import json
import boto3 
import datetime
from src.utils.logger_config import configure_logger, upload_log_to_s3, delete_log_files
from src.utils.write_csv import merge_and_upload_csv_log_to_s3
from src.quality import columns_to_use
from src.merge import read_and_concatenate_csv, read_xlsx, create_base
from src.model import main_model


# Configura el logger
current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
log_file_name = f'ejecución_{current_date}.log'
logger = configure_logger(log_file_name)

def main(log_file, bucket_name_log, files_to_execute, s3_client, cleaning_bucket,clean_folder,base_csv_name):
    
    logger.info('Inicia el proceso de verificación de calidad de datos')
    
    '''quality'''
    files_with_missing_columns, wrong_xlsx = columns_to_use(s3_client,logger,files_to_execute,cleaning_bucket,clean_folder)
    
    if files_with_missing_columns:
        logger.info('Archivos con la estructura incompleta {files_with_missing_columns}')
        logger.info('Deben contener las columnas: Active_energy, Reactive_energy, Voltaje_FA, Voltaje_FC')
        sys.exit()
    else:
        logger.info('Todos los archivos de los clientes contienen las columnas requeridas')
    
    if wrong_xlsx == 1:
        logger.info('El catalogo de sector economico esta incompleto, debe contener las columnas: Cliente:, Sector Economico:')
        sys.exit()
    else:
        logger.info('El catalogo contiene las columnas requeridas')
        
    logger.info('Inicia el merge de la data de los clientes con el catalogo de sector economico')
    
    '''merge'''
    # Leer todos los csv de clientes
    client_csv = read_and_concatenate_csv(s3_client, cleaning_bucket, clean_folder, logger)
    # leer xlsx de sector economico
    es_xlsx = read_xlsx(s3_client, cleaning_bucket, logger)
    # crear la base para el modelo
    create_base(s3_client, cleaning_bucket, stage_folder, client_csv, es_xlsx, base_csv_name, logger)
    
    
    '''model'''
    main_model(s3_client, cleaning_bucket, stage_folder, base_csv_name, logger)
    
    # Se ejecuta el proceso que actualiza o crea el archivo las fechas que han sido ejecutadas      
    merge_and_upload_csv_log_to_s3(log_file, bucket_name_log, files_to_execute, s3_client, logger)
    
    
if __name__ == "__main__":
    s3_client = boto3.client('s3')
        
    #json_arg = sys.argv[1]
    
    files = [['2021', '2024-05-11 01:33:49', '2024-05-11 01:32:20'], ['2022', '2024-05-11 01:33:50', '2024-05-11 01:32:20'], ['2023', '2024-05-11 01:33:50', '2024-05-11 01:32:20']]
    
    data_to_send = {'log_bucket':"electrodunas-log-files", 
            'log_file':"log_executed_files.csv", 
            'cleaning_bucket':"electrodunas-clean-data", 
            'clean_folder':"clean", 
            'stage_folder':"stage",
			'files_to_execute': files
			}
    
    json_arg = json.dumps(data_to_send)
    
    data = json.loads(json_arg)
    log_bucket = data['log_bucket']
    log_file = data['log_file']
    cleaning_bucket = data['cleaning_bucket']
    clean_folder = data['clean_folder']
    stage_folder = data['stage_folder']
    files_to_execute = data['files_to_execute']
    base_csv_name = 'base_clientes.csv'
    
    logger.info(f'Parametros de ejecución: log_bucket: {log_bucket} - log_file: {log_file} - cleaning_bucket: {cleaning_bucket} - clean_folder: {clean_folder} - stage_folder: {stage_folder}')
    
    if files_to_execute:
        logger.info(f'Se realizara el procesamiento de las fechas: {files_to_execute}')
        main(log_file,log_bucket,files_to_execute,s3_client,cleaning_bucket,clean_folder,base_csv_name)
        logger.info('Proceso finalizado')
        upload_log_to_s3(log_file_name, log_bucket, s3_client, logger)
    else:
        logger.info(f'No hay fechas para procesar')
        upload_log_to_s3(log_file_name, log_bucket, s3_client, logger)
        
    delete_log_files()