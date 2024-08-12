import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
from keras.models import load_model
from modules.evaluation import predict_next_months  # Certifique-se que a função existe

current_directory = os.path.dirname(os.path.abspath(__file__))
base_directory = os.path.dirname(current_directory)
MODEL_PATH = os.path.join(base_directory, "model/")

def plot_forecast(df, time_steps=3, n_months=3):
    """
    Gera gráficos das emissões de metano e produção de leite, incluindo previsões para os próximos meses.

    Parâmetros:
        df (pd.DataFrame): DataFrame contendo os dados históricos.
        time_steps (int): Número de passos de tempo usados como entrada para a previsão.
        n_months (int): Número de meses para prever.

    Retorna:
        None
    """
    # Certifique-se de que as datas estão no formato correto
    df['Period'] = pd.to_datetime(df['Period'])

    # Configurar os dados para previsão
    features = df[["Area_Used_for_Dairy_Activity", "Number_of_Lactating_Cows", "Number_of_Dry_Cows"]].values
    last_data = features[-time_steps:]  # Usar os últimos 'time_steps' como entrada

    model_milk = load_model(os.path.join(MODEL_PATH, 'model_milk.keras'))
    model_methane = load_model(os.path.join(MODEL_PATH, 'model_methane.keras'))
    scaler_target = np.load(os.path.join(MODEL_PATH, 'scaler_target.npy'), allow_pickle=True).item()
    
    # Prever os próximos meses
    next_3_months_milk = predict_next_months(model_milk, last_data, scaler_target, n_months)
    next_3_months_methane = predict_next_months(model_methane, last_data, scaler_target, n_months)

    # Inverter a normalização das previsões para trazê-las para a escala original
    next_3_months_milk = [scaler_target.inverse_transform(pred) for pred in next_3_months_milk]
    next_3_months_methane = [scaler_target.inverse_transform(pred) for pred in next_3_months_methane]

    # Preparar dados para o eixo x (datas)
    future_dates = pd.date_range(start=df['Period'].iloc[-2], periods=n_months+1, freq='M')[1:]

    # Converter future_dates para garantir que são objetos datetime
    future_dates = pd.to_datetime(future_dates)

    milk_production = df['Milk_Production'].values
    methane_emissions = df['enteric_tCO2e'].values

    # Plotar Produção de Leite
    plt.figure(figsize=(14, 7))
    plt.plot(df['Period'], milk_production, label='Produção de Leite (Histórico)', color='blue')
    plt.plot(future_dates, [pred[0][0]*0.01 for pred in next_3_months_milk], label='Previsão de Produção de Leite', color='orange')
    plt.xlabel('Período')
    plt.ylabel('Produção de Leite')
    plt.title('Produção de Leite: Histórico e Previsão')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    # Gráfico de Barras para Produção de Leite com barras mais grossas
    plt.figure(figsize=(14, 7))
    # Gráfico de barras para o histórico de produção de leite
    plt.bar(df['Period'], milk_production, label='Produção de Leite (Histórico)', color='blue', width=2, alpha=0.7)
    # Gráfico de barras para a previsão de produção de leite
    plt.bar(future_dates, [pred[0][0]*0.01 for pred in next_3_months_milk], label='Previsão de Produção de Leite', color='orange', width=2, alpha=0.7)
    plt.xlabel('Período')
    plt.ylabel('Produção de Leite')
    plt.title('Produção de Leite: Histórico e Previsão')
    plt.legend()
    plt.grid(True)
    plt.show()


    # Plotar Emissões de Metano
    plt.figure(figsize=(14, 7))
    plt.plot(df['Period'], methane_emissions, label='Emissões de Metano (Histórico)', color='green')
    plt.plot(future_dates, [pred[0][0]*0.001 for pred in next_3_months_methane], label='Previsão de Emissões de Metano', color='red')
    plt.xlabel('Período')
    plt.ylabel('Emissões de Metano (tCO2e)')
    plt.title('Emissões de Metano: Histórico e Previsão')
    plt.legend()
    plt.grid(True)
    plt.show()
