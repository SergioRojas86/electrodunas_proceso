import csv

def columns_to_use(s3_client, cleaning_bucket, clean_folder):
    
    response = s3_client.list_objects_v2(Bucket=cleaning_bucket, Prefix=clean_folder+'/', Delimiter='/')
    print(response)