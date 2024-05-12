import csv

def columns_to_use(s3_client, files_to_execute, cleaning_bucket, clean_folder):
    
    files_to_check = [f"{clean_folder}/{item[0]}/" for item in files_to_execute]
    
    response = s3_client.list_objects_v2(Bucket=cleaning_bucket, Prefix=clean_folder)
    
    if 'Contents' in response:
        for obj in response['Contents']:
            key = obj['Key']
            print(key)