#!/bin/bash

# Definir los parámetros a pasar al script Python
data_to_send="{
    \"log_bucket\": \"electrodunas-log-files\",
    \"log_file\": \"log_executed_files.csv\",
    \"cleaning_bucket\": \"electrodunas-clean-data\",
    \"clean_folder\": \"clean\",
    \"stage_folder\": \"stage\",
    \"files_to_execute\": [[\"2021\", \"2024-05-11 01:33:49\", \"2024-05-11 01:32:20\"], [\"2022\", \"2024-05-11 01:33:50\", \"2024-05-11 01:32:20\"], [\"2023\", \"2024-05-11 01:33:50\", \"2024-05-11 01:32:20\"]]
}"

# Ejecutar el script Python pasando los parámetros como un argumento JSON
python3 main.py "$data_to_send"