# train_model.py
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense 

# Função para criar as sequências temporais
def create_sequences(features, target, time_steps=3):
    X, y = [], []
    for i in range(len(features) - time_steps):
        X.append(features[i:(i + time_steps)])
        y.append(target[i + time_steps])
    return np.array(X), np.array(y)

def train_models(data, MODEL_PATH):
    # Convertendo a coluna Period para datetime e configurando como índice
    data['Period'] = pd.to_datetime(data['Period'])
    data.set_index('Period', inplace=True)

    # Selecionando as variáveis de interesse
    features = data[["Area_Used_for_Dairy_Activity", "Number_of_Lactating_Cows", "Number_of_Dry_Cows"]]
    target_milk = data['Milk_Production']
    target_methane = data['enteric_tCO2e']

    # Normalizar os dados
    scaler_features = MinMaxScaler(feature_range=(0, 1))
    scaler_target = MinMaxScaler(feature_range=(0, 1))

    scaled_features = scaler_features.fit_transform(features)
    scaled_target_milk = scaler_target.fit_transform(target_milk.values.reshape(-1, 1))
    scaled_target_methane = scaler_target.fit_transform(target_methane.values.reshape(-1, 1))

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

    # Função para construir e treinar o modelo LSTM
    def build_and_train_lstm(X_train, y_train, epochs=50, batch_size=16):
        model = Sequential()
        model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
        model.add(LSTM(units=50))
        model.add(Dense(1))

        model.compile(optimizer='adam', loss='mean_squared_error')
        model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_split=0.1, verbose=1)

        return model

    # Construir e treinar o modelo para produção de leite
    model_milk = build_and_train_lstm(X_train_milk, y_train_milk)

    # Construir e treinar o modelo para emissões de metano
    model_methane = build_and_train_lstm(X_train_methane, y_train_methane)

    # Salvar os modelos e os escaladores
    model_milk.save(os.path.join(MODEL_PATH, 'model_milk.keras'))
    model_methane.save(os.path.join(MODEL_PATH, 'model_methane.keras'))
    np.save(os.path.join(MODEL_PATH, 'scaler_features.npy'), scaler_features)
    np.save(os.path.join(MODEL_PATH, 'scaler_target.npy'), scaler_target)
    np.save(os.path.join(MODEL_PATH, 'X_test_milk.npy'), X_test_milk)
    np.save(os.path.join(MODEL_PATH, 'X_test_methane.npy'), X_test_methane)
    np.save(os.path.join(MODEL_PATH, 'y_test_milk.npy'), y_test_milk)
    np.save(os.path.join(MODEL_PATH, 'y_test_methane.npy'), y_test_methane)