import logging
import os

def configure_logger(log_file_name):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler(log_file_name)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

def upload_to_s3(log_file_name, bucket_name_log, s3_client):
    folder_name = 'execution-log'
    object_name = os.path.join(folder_name, os.path.basename(log_file_name))
    
    s3_client.upload_file(log_file_name, bucket_name_log, log_file_name)
    print(f"El archivo {log_file_name} ha sido subido exitosamente al bucket {bucket_name_log}.")