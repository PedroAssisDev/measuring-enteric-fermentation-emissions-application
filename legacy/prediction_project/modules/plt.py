import os
import pandas as pd
import matplotlib.pyplot as plt

def plot_property_data(data, property_name, save_path, model_milk, model_methane, scalers):
    # Filtrar dados para a propriedade específica
    property_data = data[data["Property"] == property_name].copy()
    
    # Convertendo a coluna Period para datetime e configurando como índice
    property_data['Period'] = pd.to_datetime(property_data['Period'])
    property_data.set_index('Period', inplace=True)
    
    # Selecionando as variáveis de interesse
    features = property_data[["Area_Used_for_Dairy_Activity", "Number_of_Lactating_Cows", "Number_of_Dry_Cows"]]
    
    # Normalizar os dados
    scaled_features = scalers['features'].transform(features)
    
    # Prever os próximos dois meses para produção de leite
    X_last_milk = scaled_features[-3:].reshape(1, 3, -1)  # Adicionar dimensão de lote
    milk_predictions = model_milk.predict(X_last_milk)
    milk_predictions_real = scalers['target_milk'].inverse_transform(milk_predictions)
    
    # Prever os próximos dois meses para emissões de metano
    X_last_methane = scaled_features[-3:].reshape(1, 3, -1)  # Adicionar dimensão de lote
    methane_predictions = model_methane.predict(X_last_methane)
    methane_predictions_real = scalers['target_methane'].inverse_transform(methane_predictions)
    
    # Verificar o comprimento das previsões
    future_periods = pd.date_range(property_data.index[-1], periods=2, freq='M')[1:]  # Os dois próximos meses
    if len(milk_predictions_real.flatten()) != len(future_periods):
        print(f"Erro: O comprimento das previsões de leite ({len(milk_predictions_real.flatten())}) não corresponde ao número de períodos futuros ({len(future_periods)})")
    if len(methane_predictions_real.flatten()) != len(future_periods):
        print(f"Erro: O comprimento das previsões de metano ({len(methane_predictions_real.flatten())}) não corresponde ao número de períodos futuros ({len(future_periods)})")

    # Adicionar previsões aos dados
    milk_forecast_df = pd.DataFrame({'Period': future_periods, 'Milk_Production': milk_predictions_real.flatten()})
    methane_forecast_df = pd.DataFrame({'Period': future_periods, 'enteric_tCO2e': methane_predictions_real.flatten()})
    milk_forecast_df.set_index('Period', inplace=True)
    methane_forecast_df.set_index('Period', inplace=True)

    # Configurar gráfico
    plt.figure(figsize=(12, 6))

    # Plotar Produção de Leite
    plt.subplot(2, 1, 1)
    plt.plot(property_data.index, property_data['Milk_Production'], marker='o', color='blue', label='Milk Production')
    plt.plot(milk_forecast_df.index, milk_forecast_df['Milk_Production'], marker='o', color='yellow', label='Milk Forecast')
    plt.title(f'Property: {property_name} - Milk Production')
    plt.xlabel('Period')
    plt.ylabel('Milk Production (liters)')
    plt.grid(True)
    plt.legend()

    # Plotar Emissões de Metano
    plt.subplot(2, 1, 2)
    plt.plot(property_data.index, property_data['enteric_tCO2e'], marker='o', color='blue', label='Methane Emissions')
    plt.plot(methane_forecast_df.index, methane_forecast_df['enteric_tCO2e'], marker='o', color='yellow', label='Methane Forecast')
    plt.title(f'Property: {property_name} - Methane Emissions')
    plt.xlabel('Period')
    plt.ylabel('Methane Emissions (tCO2e)')
    plt.grid(True)
    plt.legend()

    # Ajustar layout
    plt.tight_layout()

    # Salvar gráfico
    os.makedirs(save_path, exist_ok=True)
    plt.savefig(os.path.join(save_path, f'property_{property_name}_plots.png'))
    plt.close()

    print(f'Gráfico para {property_name} salvo em {save_path}')

def plot_all_properties(data, models, save_path):
    # Listar todas as propriedades únicas
    properties = data["Property"].unique()

    # Gerar gráficos para cada propriedade
    for property_name in properties:
        plot_property_data(data, property_name, save_path, 
                           models['milk'][property_name], 
                           models['methane'][property_name], 
                           models['scalers'][property_name])
