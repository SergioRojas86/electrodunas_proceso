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

def upload_log_to_s3(log_file_name, bucket_name_log, s3_client, logger_com):
    folder_name = 'execution-log'
    object_name = os.path.join(folder_name, os.path.basename(log_file_name))
    
    s3_client.upload_file(log_file_name, bucket_name_log, object_name)
    
    logger_com.info(f"El archivo {log_file_name} ha sido subido exitosamente al bucket {bucket_name_log}.")    
    print(f"El archivo {log_file_name} ha sido subido exitosamente al bucket {bucket_name_log}.")
    
    
def delete_log_files(folder_path='./'):
    try:
        for filename in os.listdir(folder_path):
            if filename.endswith(".log"):
                file_path = os.path.join(folder_path, filename)
                os.remove(file_path)
                print(f"Archivo eliminado: {file_path}")
    except Exception as e:
        print(f"Error al eliminar archivos: {e}")