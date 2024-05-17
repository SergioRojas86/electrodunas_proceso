import pandas as pd
from io import BytesIO


# Función para leer y concatenar CSVs
def read_and_concatenate_csv(s3_client, cleaning_bucket, clean_folder, logger):
    combined_df = pd.DataFrame()
    directory = f'{clean_folder}/'
    response = s3_client.list_objects_v2(Bucket=cleaning_bucket, Prefix=directory)
    if 'Contents' in response:
        for obj in response['Contents']:
            key = obj['Key']
            if key.endswith('.csv'):
                response = s3_client.get_object(Bucket=cleaning_bucket, Key=key)
                data = response['Body'].read()
                df = pd.read_csv(BytesIO(data))
                combined_df = pd.concat([combined_df, df], ignore_index=True)
    combined_df = combined_df.drop(columns=['Año'])
    return combined_df

# Función para leer el archivo XLSX
def read_xlsx(s3_client, cleaning_bucket, logger):
    key = 'clean/sector_economico_clientes.xlsx'
    response = s3_client.get_object(Bucket=cleaning_bucket, Key=key)
    data = response['Body'].read()
    xlsx_df = pd.read_excel(BytesIO(data), engine='openpyxl')
    xlsx_df = xlsx_df.rename(columns={'Cliente:': 'Cliente', 'Sector Económico:': 'Sector_Economico'})
    xlsx_df['Cliente'] = xlsx_df['Cliente'].str.strip()
    return xlsx_df

def create_base(s3_client, cleaning_bucket, stage_folder, client_csv, es_xlsx, logger):
    # Realizar el join
    final_df = pd.merge(client_csv, es_xlsx, on='Cliente', how='left')
    
    final_df['Fecha'] = pd.to_datetime(final_df['Fecha'])
    
    # Ordenar el DataFrame por las columnas 'fecha' y 'Cliente'
    final_df = final_df.sort_values(by=['Cliente','Fecha'])
    
    # Guardar el resultado en un nuevo CSV en s3
    output_key = f'{stage_folder}/combined_output.csv'
    csv_buffer = BytesIO()
    final_df.to_csv(csv_buffer, index=False)
    s3_client.put_object(Bucket=cleaning_bucket, Key=output_key, Body=csv_buffer.getvalue())
    
    print(final_df)