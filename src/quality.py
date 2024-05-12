import csv

def columns_to_use(s3_client, files_to_execute, cleaning_bucket, clean_folder):
    
    
    for file in files_to_execute:
        print(file[0])
    #response = s3_client.list_objects_v2(Bucket=cleaning_bucket, Prefix=clean_folder+'/', Delimiter='/')
    #print(response)