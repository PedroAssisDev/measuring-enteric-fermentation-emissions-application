import os
from modules.data_loader import load_data
from modules.lstm_model import train_and_select_best_model
import os
import pandas as pd
from modules.plt import plot_all_properties
from keras.models import load_model
import numpy as np

current_directory = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(current_directory, "data/property_data_standardized.csv")
MODEL_PATH = os.path.join(current_directory, "model/")
PLOT_PATH = os.path.join(current_directory, "plots/")


def main():
    # Criação da pasta para modelos se não existir
    os.makedirs(MODEL_PATH, exist_ok=True)

    # Carrega os dados
    data = load_data(DATA_PATH)
    data = data[data["Property"].isin(["P-12", "P-22"])]
    # Listar todas as propriedades únicas
    properties = data["Property"].unique()

    # Definir intervalos de hiperparâmetros para busca
    lstm_units_list = [50, 100]
    epochs_list = [50, 100]
    batch_size_list = [16, 32]

    # # Treinar e selecionar o melhor modelo para cada propriedade
    for property_name in properties:
        print(property_name)
    #     train_and_select_best_model(data, property_name, MODEL_PATH, lstm_units_list, epochs_list, batch_size_list)
    
    # Gerar gráficos para todas as propriedades
    # Carregar modelos e escaladores para as propriedades
    models = {'milk': {}, 'methane': {} , 'scalers': {} }
    for property_name in properties:
        scalers = {
            'features': np.load(os.path.join(MODEL_PATH + f"{property_name}", f'scaler_features_{property_name}.npy'), allow_pickle=True).item(),
            'target_methane': np.load(os.path.join(MODEL_PATH + f"{property_name}", f'scaler_target_methane_{property_name}.npy'), allow_pickle=True).item(),
            'target_milk': np.load(os.path.join(MODEL_PATH + f"{property_name}", f'scaler_target_milk_{property_name}.npy'), allow_pickle=True).item()
        }
        models['milk'][property_name] = load_model(os.path.join(MODEL_PATH, f"{property_name}", f'best_model_milk_{property_name}.keras'))
        models['methane'][property_name] = load_model(os.path.join(MODEL_PATH, f"{property_name}", f'best_model_methane_{property_name}.keras'))
        models['scalers'][property_name] = scalers

    # Gerar gráficos para todas as propriedades
    plot_all_properties(data,models, PLOT_PATH)

if __name__ == "__main__":
    main()
    
    
