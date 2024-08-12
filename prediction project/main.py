import os
from modules.data_loader import load_data
from modules.lstm_model import train_models
from modules.evaluation import validate_models
from modules.plt import plot_forecast

current_directory = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(current_directory, "data/property_data_standardized.csv")
MODEL_PATH = os.path.join(current_directory, "model/")

def main():
    # Criação da pasta para modelos se não existir
    os.makedirs(MODEL_PATH, exist_ok=True)

    # Carrega os dados
    data = load_data(DATA_PATH)
    
    #train_models(data[data["Property"] == "P-22"], MODEL_PATH)
    
    #validate_models(MODEL_PATH)
    plot_forecast(data[data["Property"] == "P-22"])
    
    
    

if __name__ == "__main__":
    main()
