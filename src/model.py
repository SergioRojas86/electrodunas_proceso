import pandas as pd
from io import BytesIO
from scipy.stats import boxcox
from scipy.special import inv_boxcox
import seaborn as sns
from statsmodels.tsa.arima.model import ARIMA
from sklearn.ensemble import IsolationForest
import numpy as np
import pickle
import holidays

import warnings

# Ignorar específicamente FutureWarning
warnings.filterwarnings('ignore', category=FutureWarning)

def read_base(s3_client, cleaning_bucket, stage_folder, base_csv_name, logger):
    file = f'{stage_folder}/{base_csv_name}'
    response = s3_client.get_object(Bucket=cleaning_bucket, Key=file)
    data = response['Body'].read()
    df = pd.read_csv(BytesIO(data))
    return df

def anomalies(data):
    data['is_outlier_if'] = False  

    for cliente, group in data.groupby('Cliente'):
        X = group['Active_energy'].values.reshape(-1, 1)
        
        # Isolation Forest
        if_model = IsolationForest(contamination='auto')
        preds_if = if_model.fit_predict(X)
        data.loc[group.index, 'is_outlier_if'] = (preds_if == -1)  # -1 es True para outliers
        
    return data

def modified_data(anomaly_data):
    Data_ajustado = anomaly_data.copy()
    Data_ajustado['Fecha'] = pd.to_datetime(Data_ajustado['Fecha']).dt.date

    Data_ajustado.reset_index(inplace=True)

    condicion_no_outliers = ~Data_ajustado['is_outlier_if']
    media_diaria = Data_ajustado[condicion_no_outliers].groupby(['Cliente', 'Fecha'])['Active_energy'].mean().reset_index(name='Media_Diaria')

    Data_ajustado = Data_ajustado.merge(media_diaria, on=['Cliente', 'Fecha'], how='left')
    Data_ajustado.loc[Data_ajustado['is_outlier_if'], 'Active_energy'] = Data_ajustado.loc[Data_ajustado['is_outlier_if'], 'Media_Diaria']
    Data_ajustado['Active_energy'].fillna(Data_ajustado['Active_energy'].mean(), inplace=True)
    
    Data_ajustado['Fecha'] = anomaly_data['Fecha']
    Data_ajustado = Data_ajustado.drop(['index'], axis=1)
    
    return Data_ajustado
    
def box_cox(Data_ajustado):
    #  todos los valores en 'Active_energy' sean positivos
    Data_ajustado['Active_energy'] = Data_ajustado['Active_energy'].clip(lower=0.001)  # Usar un pequeño valor positivo para reemplazar 0 o valores negativos

    # Aplicar la transformación Box-Cox
    Data_ajustado['Transformed_Active_energy'], fitted_lambda = boxcox(Data_ajustado['Active_energy'])
    
    return Data_ajustado

# Guardar el modelo ARIMA en S3
def save_model_to_s3(resultado, cliente, s3_client, cleaning_bucket, models_folder):
    buffer = BytesIO()
    pickle.dump(resultado, buffer)
    buffer.seek(0)
    s3_client.put_object(Bucket=cleaning_bucket, Key=f'{models_folder}/modelo_arima_{cliente}.pkl', Body=buffer.getvalue())

    

def main_model(s3_client, cleaning_bucket, stage_folder, base_csv_name, logger):
    
    base_df = read_base(s3_client, cleaning_bucket, stage_folder, base_csv_name, logger)
    
    anomaly_data = anomalies(base_df)
    
    Data_ajustado = modified_data(anomaly_data)
    
    Data_ajustado_bc = box_cox(Data_ajustado)
    
    for cliente in Data_ajustado_bc['Cliente'].unique():
        data_cliente = Data_ajustado_bc[Data_ajustado_bc['Cliente'] == cliente]
        data_cliente.set_index('Fecha', inplace=True, drop=False)
        data_cliente.sort_index(inplace=True)

        train = data_cliente.iloc[:-500]  
        test = data_cliente.iloc[-500:]  

        # Ajustar el modelo ARIMA
        modelo = ARIMA(train['Transformed_Active_energy'], order=(2,2,2))
        resultado = modelo.fit()
        
        print(f'model: modelo_arima_{cliente}')
        # Guardar el modelo ajustado en S3
        save_model_to_s3(resultado, cliente, s3_client, cleaning_bucket, models_folder='models')