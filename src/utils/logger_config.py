import logging
import datetime

def configure_logger(log_file_name):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")  # Obtener la fecha actual y formatearla
    file_handler = logging.FileHandler(log_file_name)  # Utilizar la fecha en el nombre del archivo
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

def upload_to_s3(log_file_name, bucket_name_log):
    folder_name = 'execution-log'
    s3 = boto3.client('s3')
    object_name = os.path.join(folder_name, os.path.basename(log_file_name))
    
    s3.upload_file(log_file_name, bucket_name_log, object_name)
    print(f"El archivo {log_file_name} ha sido subido exitosamente al bucket {bucket_name_log}.")