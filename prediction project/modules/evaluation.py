import os
import numpy as np
from keras.models import load_model
from sklearn.metrics import mean_squared_error

# Função para prever os próximos 3 meses
def predict_next_months(model, last_data, scaler_target, n_months):
    predictions = []
    current_input = last_data.copy()

    for _ in range(n_months):
        next_pred = model.predict(current_input[np.newaxis, :, :])
        # Inverter a normalização para obter o valor real
        next_pred_real = scaler_target.inverse_transform(next_pred)
        predictions.append(next_pred_real)

        # Ajustar next_pred para ter a mesma quantidade de features que current_input
        next_pred_adjusted = np.tile(next_pred[0], (current_input.shape[1], 1)).T
        current_input = np.append(current_input[1:], next_pred_adjusted, axis=0)
    
    return predictions

# Função para realizar a validação
# Função para realizar a validação
def validate_models(MODEL_PATH):
    # Carregar os modelos e os dados
    model_milk = load_model(os.path.join(MODEL_PATH, 'model_milk.keras'))
    model_methane = load_model(os.path.join(MODEL_PATH, 'model_methane.keras'))
    
    scaler_features = np.load(os.path.join(MODEL_PATH, 'scaler_features.npy'), allow_pickle=True).item()
    scaler_target = np.load(os.path.join(MODEL_PATH, 'scaler_target.npy'), allow_pickle=True).item()
    X_test_milk = np.load(os.path.join(MODEL_PATH, 'X_test_milk.npy'))
    X_test_methane = np.load(os.path.join(MODEL_PATH, 'X_test_methane.npy'))
    y_test_milk = np.load(os.path.join(MODEL_PATH, 'y_test_milk.npy'))
    y_test_methane = np.load(os.path.join(MODEL_PATH, 'y_test_methane.npy'))

    # Prever os próximos 3 meses
    next_3_months_milk = predict_next_months(model_milk, X_test_milk[-1], scaler_target, 3)
    next_3_months_methane = predict_next_months(model_methane, X_test_methane[-1], scaler_target, 3)

    # Avaliar o modelo
    rmse_milk = np.sqrt(mean_squared_error(y_test_milk, model_milk.predict(X_test_milk)))
    rmse_methane = np.sqrt(mean_squared_error(y_test_methane, model_methane.predict(X_test_methane)))

    print(f'RMSE para a Produção de Leite: {rmse_milk}')
    print(f'RMSE para as Emissões de Metano: {rmse_methane}')

    # Exibir as previsões e valores reais para os próximos 3 meses
    print('\nPrevisões e Valores Reais para os Próximos 3 Meses:')
    for i, (milk_pred, methane_pred) in enumerate(zip(next_3_months_milk, next_3_months_methane), 1):
        real_milk = scaler_target.inverse_transform(y_test_milk[-3+i].reshape(1, -1))
        real_methane = scaler_target.inverse_transform(y_test_methane[-3+i].reshape(1, -1))

        print(f'Previsão do mês {i}:')
        print(f' - Produção de Leite: Previsão = {milk_pred[0][0]:.2f}, Real = {real_milk[0][0]:.2f}')
        print(f' - Emissões de Metano: Previsão = {methane_pred[0][0]:.2f}, Real = {real_methane[0][0]:.2f}')
        print('---')
        

