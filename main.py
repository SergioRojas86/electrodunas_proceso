import sys
import json
from src.utils.logger_config import configure_logger, upload_to_s3
import boto3import datetime

# Configura el logger
current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
log_file_name = f'ejecución_{current_date}.log'
logger = configure_logger(log_file_name)

def main():
    json_arg = sys.argv[1]
    data = json.loads(json_arg)
    
    files_to_execute = data['files_to_execute']
    logger.info(f'Se realizara el procesamiento de las fechas: {files_to_execute}')
    
    
if __name__ == "__main__":
    s3_client = boto3.client('s3')
    main()
    bucket_name_log = 'electrodunas-log-files'
    upload_to_s3(log_file_name, bucket_name_log, s3_client)