import logging
import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")  # Obtener la fecha actual y formatearla
file_handler = logging.FileHandler(f'registro_{current_date}.log')  # Utilizar la fecha en el nombre del archivo
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
