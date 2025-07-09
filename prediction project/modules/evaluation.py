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
