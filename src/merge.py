import pandas as pd
from io import BytesIO


# Función para leer y concatenar CSVs
def read_and_concatenate_csv(s3_client, cleaning_bucket, logger):
    combined_df = None
    directory = 'clean/'
    response = s3_client.list_objects_v2(Bucket=cleaning_bucket, Prefix=directory)
    if 'Contents' in response:
        for obj in response['Contents']:
            key = obj['Key']
            if key.endswith('.csv'):
                response = s3_client.get_object(Bucket=cleaning_bucket, Key=key)
                data = response['Body'].read()
                if combined_df is None:
                    combined_df = pd.read_csv(BytesIO(data))  # Leer el primer CSV con encabezado
                else:
                    df = pd.read_csv(BytesIO(data), header=None)  # Leer los siguientes CSV sin encabezado
                    df.columns = combined_df.columns  # Asignar las columnas para mantener la consistencia
                    combined_df = pd.concat([combined_df, df], ignore_index=True)
    print(combined_df)
    #return combined_df

# Función para leer el archivo XLSX
def read_xlsx(s3_client, cleaning_bucket, key):
    response = s3_client.get_object(Bucket=cleaning_bucket, Key=key)
    data = response['Body'].read()
    xlsx_df = pd.read_excel(BytesIO(data), engine='openpyxl')
    xlsx_df = xlsx_df.rename(columns={'Cliente:': 'Cliente', 'Sector Económico:': 'Sector Economico'})
    xlsx_df['Cliente'] = xlsx_df['Cliente'].str.strip()
    return xlsx_df

'''
# Función principal
def main():
    # Leer y concatenar todos los CSVs
    combined_csv_df = read_and_concatenate_csvs(s3_client, cleaning_bucket, directories_to_check)
    
    # Leer el archivo XLSX
    sector_economico_df = read_xlsx(s3_client, cleaning_bucket, f'{clean_folder}sector_economico_clientes.xlsx')
    
    # Realizar el join
    final_df = pd.merge(combined_csv_df, sector_economico_df, on='Cliente', how='left')
    
    # Guardar el resultado en un nuevo CSV
    output_key = f'{clean_folder}combined_output.csv'
    csv_buffer = BytesIO()
    final_df.to_csv(csv_buffer, index=False)
    s3_client.put_object(Bucket=cleaning_bucket, Key=output_key, Body=csv_buffer.getvalue())

    print(f"Archivo combinado guardado en {output_key}")
'''