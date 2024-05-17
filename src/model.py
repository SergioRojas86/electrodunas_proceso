import pandas as pd
from io import BytesIO

def read_base(s3_client, cleaning_bucket, stage_folder, base_csv_name, logger):
    file = f'{stage_folder}/{base_csv_name}'
    response = s3_client.get_object(Bucket=cleaning_bucket, Key=file)
    data = response['Body'].read()
    df = pd.read_csv(BytesIO(data))
    print(df)


def main_model(s3_client, cleaning_bucket, stage_folder, base_csv_name, logger):
    
    read_base(s3_client, cleaning_bucket, stage_folder, base_csv_name, logger)