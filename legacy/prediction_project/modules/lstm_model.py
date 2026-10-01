import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense
from sklearn.metrics import mean_squared_error
from itertools import product

# Função para criar sequências temporais
def create_sequences(features, target, time_steps=3):
    X, y = [], []
    for i in range(len(features) - time_steps):
        X.append(features[i:(i + time_steps)])
        y.append(target[i + time_steps])
    return np.array(X), np.array(y)

# Função para construir e treinar o modelo LSTM
def build_and_train_lstm(X_train, y_train, lstm_units=50, epochs=50, batch_size=16):
    model = Sequential()
    model.add(LSTM(units=lstm_units, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(LSTM(units=lstm_units))
    model.add(Dense(1))

    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_split=0.1, verbose=0)
    
    return model

# Função para realizar validação cruzada e salvar o melhor modelo
def train_and_select_best_model(data, property_name, model_path, lstm_units_list, epochs_list, batch_size_list):
    # Filtrar dados para a propriedade específica
    property_data = data[data["Property"] == property_name]

    # Convertendo a coluna Period para datetime e configurando como índice
    property_data['Period'] = pd.to_datetime(property_data['Period'])
    property_data.set_index('Period', inplace=True)

    # Selecionando as variáveis de interesse
    features = property_data[["Area_Used_for_Dairy_Activity", "Number_of_Lactating_Cows", "Number_of_Dry_Cows"]]
    target_milk = property_data['Milk_Production']
    target_methane = property_data['enteric_tCO2e']

    # Normalizar os dados
    scaler_features = MinMaxScaler(feature_range=(0, 1))
    scaler_target_milk = MinMaxScaler(feature_range=(0, 1))
    scaler_target_methane = MinMaxScaler(feature_range=(0, 1))

    scaled_features = scaler_features.fit_transform(features)
    scaled_target_milk = scaler_target_milk.fit_transform(target_milk.values.reshape(-1, 1))
    scaled_target_methane = scaler_target_methane.fit_transform(target_methane.values.reshape(-1, 1))

    # Criando sequências com 3 meses de histórico para previsão
    time_steps = 3
    X_milk, y_milk = create_sequences(scaled_features, scaled_target_milk, time_steps)
    X_methane, y_methane = create_sequences(scaled_features, scaled_target_methane, time_steps)

    # Dividindo em conjuntos de treino e teste
    split = int(0.8 * len(X_milk))
    X_train_milk, X_test_milk = X_milk[:split], X_milk[split:]
    y_train_milk, y_test_milk = y_milk[:split], y_milk[split:]

    X_train_methane, X_test_methane = X_methane[:split], X_methane[split:]
    y_train_methane, y_test_methane = y_methane[:split], y_methane[split:]

    # Gerar todas as combinações possíveis de hiperparâmetros
    best_rmse_milk = float('inf')
    best_rmse_methane = float('inf')
    best_model_milk = None
    best_model_methane = None
    best_params_milk = None
    best_params_methane = None

    for lstm_units, epochs, batch_size in product(lstm_units_list, epochs_list, batch_size_list):
        # Treinar o modelo para produção de leite
        model_milk = build_and_train_lstm(X_train_milk, y_train_milk, lstm_units, epochs, batch_size)
        rmse_milk = np.sqrt(mean_squared_error(y_test_milk, model_milk.predict(X_test_milk)))

        # Salvar o melhor modelo de leite
        if rmse_milk < best_rmse_milk:
            best_rmse_milk = rmse_milk
            best_model_milk = model_milk
            best_params_milk = (lstm_units, epochs, batch_size)

        # Treinar o modelo para emissões de metano
        model_methane = build_and_train_lstm(X_train_methane, y_train_methane, lstm_units, epochs, batch_size)
        rmse_methane = np.sqrt(mean_squared_error(y_test_methane, model_methane.predict(X_test_methane)))

        # Salvar o melhor modelo de metano
        if rmse_methane < best_rmse_methane:
            best_rmse_methane = rmse_methane
            best_model_methane = model_methane
            best_params_methane = (lstm_units, epochs, batch_size)

    # Criar diretório para a propriedade
    property_model_path = os.path.join(model_path, property_name)
    os.makedirs(property_model_path, exist_ok=True)

    # Salvar o melhor modelo e escaladores com o nome da propriedade
    best_model_milk.save(os.path.join(property_model_path, f'best_model_milk_{property_name}.keras'))
    best_model_methane.save(os.path.join(property_model_path, f'best_model_methane_{property_name}.keras'))
    np.save(os.path.join(property_model_path, f'scaler_features_{property_name}.npy'), scaler_features)
    np.save(os.path.join(property_model_path, f'scaler_target_milk_{property_name}.npy'), scaler_target_milk)
    np.save(os.path.join(property_model_path, f'scaler_target_methane_{property_name}.npy'), scaler_target_methane)
    np.save(os.path.join(property_model_path, f'best_params_milk_{property_name}.npy'), best_params_milk)
    np.save(os.path.join(property_model_path, f'best_params_methane_{property_name}.npy'), best_params_methane)

    print(f'Melhor modelo para {property_name} salvo com RMSE Leite: {best_rmse_milk}, RMSE Metano: {best_rmse_methane}')
