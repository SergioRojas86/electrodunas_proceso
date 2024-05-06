import sys
import json
import src.utils.logger_config

def main():
    json_arg = sys.argv[1]
    data = json.loads(json_arg)
    
    files_to_execute = data['files_to_execute']
    logger_config.logger.info(f'Se realizara el procesamiento de las fechas: {files_to_execute}')
    
    
if __name__ == "__main__":
    main()