import os
import numpy as np
import pandas as pd
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

# Função para carregar e preparar dados
def load_and_prepare_data(filepath):
    df = pd.read_csv(filepath, sep=";")
    df['Period'] = pd.to_datetime(df['Period'])
    return df

# Função para carregar modelos e escaladores
def load_models_and_scalers(model_dir, property_name):
    model_milk_path = os.path.join(model_dir, f'{property_name}/best_model_milk_{property_name}.keras')
    model_methane_path = os.path.join(model_dir, f'{property_name}/best_model_methane_{property_name}.keras')
    scaler_features_path = os.path.join(model_dir, f'{property_name}/scaler_features_{property_name}.npy')
    scaler_target_milk_path = os.path.join(model_dir, f'{property_name}/scaler_target_milk_{property_name}.npy')
    scaler_target_methane_path = os.path.join(model_dir, f'{property_name}/scaler_target_methane_{property_name}.npy')

    model_milk = load_model(model_milk_path)
    model_methane = load_model(model_methane_path)
    scaler_features = np.load(scaler_features_path, allow_pickle=True).item()
    scaler_target_milk = np.load(scaler_target_milk_path, allow_pickle=True).item()
    scaler_target_methane = np.load(scaler_target_methane_path, allow_pickle=True).item()

    return [model_milk, model_methane], [scaler_features, scaler_target_milk, scaler_target_methane]

# Função para gerar previsões
def generate_predictions(models, scalers, features):
    model_milk, model_methane = models[0], models[1]
    scaler_target_milk, scaler_target_methane = scalers[1], scalers[2]

    scaled_features = scalers[0].transform(features)
    predictions_milk = []
    predictions_methane = []
    input_seq = np.expand_dims(scaled_features, axis=0)

    for _ in range(3):
        pred_milk = model_milk.predict(input_seq)
        predictions_milk.append(pred_milk[0, 0])

        pred_methane = model_methane.predict(input_seq)
        predictions_methane.append(pred_methane[0, 0])

        next_input = np.concatenate((input_seq[:, 1:, :], np.repeat(pred_milk.reshape(1, 1, 1), repeats=input_seq.shape[2], axis=2)), axis=1)
        input_seq = next_input

    predictions_milk = scaler_target_milk.inverse_transform(np.array(predictions_milk).reshape(-1, 1))
    predictions_methane = scaler_target_methane.inverse_transform(np.array(predictions_methane).reshape(-1, 1))

    return predictions_milk.flatten(), predictions_methane.flatten()

# Função para criar o layout do aplicativo
def create_layout(app, properties):
    return dbc.Container([
        html.H1("Milk Production and Carbon Emissions Analysis", className="text-center mt-4 mb-4"),

        dbc.Row([
            dbc.Col(create_property_dropdown(properties), md=3),
            dbc.Col(create_period_picker(), md=3),
            dbc.Col(create_prediction_button(), md=3),
        ]),

        dbc.Row([
            dbc.Col(html.Div(id='kpi-cards'), md=12),
        ]),

        dbc.Row([
            dbc.Col(dcc.Graph(id='milk-prediction-bar-chart'), md=6),
            dbc.Col(dcc.Graph(id='methane-prediction-bar-chart'), md=6),
        ]),

        create_prediction_modal()
    ], fluid=True)

# Função para criar dropdown de propriedades
def create_property_dropdown(properties):
    return html.Div([
        dbc.Label("Select Property", html_for="property-dropdown"),
        dcc.Dropdown(
            id="property-dropdown",
            options=[{'label': prop, 'value': prop} for prop in properties],
            value=properties[0],
            multi=False,
            clearable=False,
        ),
    ], className="mb-4")

# Função para criar seletor de período
def create_period_picker():
    return html.Div([
        dbc.Label("Select Period Range", html_for="period-picker"),
        dcc.DatePickerRange(
            id='period-picker',
            start_date=df['Period'].min(),
            end_date=df['Period'].max(),
            display_format='YYYY-MM'
        ),
    ], className="mb-4")

# Função para criar botão de previsão
def create_prediction_button():
    return html.Div([
        dbc.Button("Generate Prediction", id="open-prediction-modal", color="primary"),
    ])

# Função para criar modal de previsão
def create_prediction_modal():
    return html.Div([
        dbc.Modal([
            dbc.ModalHeader("3-Month Forecast"),
            dbc.ModalBody([
                dcc.Graph(id="milk-prediction-bar-chart"),
                dcc.Graph(id="methane-prediction-bar-chart"),
            ]),
            dbc.ModalFooter(
                dbc.Button("Close", id="close-prediction-modal", className="ms-auto")
            ),
        ], id="prediction-modal", size="lg"),
    ])

# Inicializar o aplicativo Dash
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])

# Carregar dados
data_path = '/home/pedro_estudos/Documentos/GitHub/measuring-enteric-fermentation-emissions-application/dashboard/data/property_data.csv'
df = load_and_prepare_data(data_path)

# Definir layout do aplicativo
app.layout = create_layout(app, df["Property"].unique())

# Callback para abrir e fechar o modal de previsão
@app.callback(
    Output("prediction-modal", "is_open"),
    [Input("open-prediction-modal", "n_clicks"), Input("close-prediction-modal", "n_clicks")],
    [State("prediction-modal", "is_open")]
)
def toggle_prediction_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# Callback para gerar e exibir as previsões nos gráficos de barras
@app.callback(
    [Output("milk-prediction-bar-chart", "figure"),
     Output("methane-prediction-bar-chart", "figure")],
    [Input("property-dropdown", "value"),
     Input("period-picker", "start_date"),
     Input("period-picker", "end_date")]
)
def update_prediction_graph(selected_property, start_date, end_date):
    model_dir = '/home/pedro_estudos/Documentos/GitHub/measuring-enteric-fermentation-emissions-application/prediction project/model/'
    models, scalers = load_models_and_scalers(model_dir, selected_property)

    # Filtrar os dados com base no intervalo de datas selecionado
    filtered_data = df[(df["Property"] == selected_property) & 
                       (df["Period"] >= start_date) & 
                       (df["Period"] <= end_date)].sort_values(by="Period")
    
    recent_data = filtered_data.tail(3)
    features = recent_data[["Area_Used_for_Dairy_Activity", "Number_of_Lactating_Cows", "Number_of_Dry_Cows"]]

    # Gerar previsões
    predictions_milk, predictions_methane = generate_predictions(models, scalers, features)

    # Criar datas futuras para o gráfico
    forecast_periods = pd.date_range(recent_data["Period"].max(), periods=4, freq='M')[1:]
    forecast_periods = forecast_periods.strftime('%Y-%m')

    # Dados reais (anteriores)
    actual_periods = filtered_data["Period"].dt.strftime('%Y-%m')
    actual_milk = filtered_data["Milk_Production"]
    actual_methane = filtered_data["enteric_tCO2e"]

    # Gráfico de barras para produção de leite
    # Definindo uma paleta de cores sofisticada
    colors = ['#636EFA', '#EF553B']

    # Gráfico de barras para produção de leite
    milk_fig = go.Figure()
    milk_fig.add_trace(go.Bar(
        x=actual_periods, 
        y=actual_milk, 
        name="Real Milk Production", 
        marker_color=colors[0],
        opacity=0.8
    ))
    milk_fig.add_trace(go.Bar(
        x=forecast_periods, 
        y=predictions_milk, 
        name="Milk Production Forecast", 
        marker_color=colors[1],
        opacity=0.7
    ))
    milk_fig.update_layout(
        title=f"<b>Milk Production - {selected_property}</b>",
        title_x=0.5,  # Centraliza o título
        xaxis_title="<b>Period</b>",
        yaxis_title="<b>Liters</b>",
        barmode='group',
        font=dict(size=14, color="black", family="Arial"),
        legend=dict(
            title="<b>Legend</b>",
            orientation="h",  # Horizontal
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        ),
        xaxis=dict(tickangle=-45, showgrid=True, gridcolor='LightGray'),
        yaxis=dict(showgrid=True, gridcolor='LightGray'),
        margin=dict(l=40, r=40, t=60, b=40),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    # Gráfico de barras para emissões de metano
    methane_fig = go.Figure()
    methane_fig.add_trace(go.Bar(
        x=actual_periods, 
        y=actual_methane, 
        name="Real Methane Emissions", 
        marker_color=colors[0],
        opacity=0.8
    ))
    methane_fig.add_trace(go.Bar(
        x=forecast_periods, 
        y=predictions_methane, 
        name="Methane Emissions Forecast", 
        marker_color=colors[1],
        opacity=0.7
    ))
    methane_fig.update_layout(
        title=f"<b>Methane Emissions - {selected_property}</b>",
        title_x=0.5,  # Centraliza o título
        xaxis_title="<b>Period</b>",
        yaxis_title="<b>tCO2e</b>",
        barmode='group',
        font=dict(size=14, color="black", family="Arial"),
        legend=dict(
            title="<b>Legend</b>",
            orientation="h",  # Horizontal
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        ),
        xaxis=dict(tickangle=-45, showgrid=True, gridcolor='LightGray'),
        yaxis=dict(showgrid=True, gridcolor='LightGray'),
        margin=dict(l=40, r=40, t=60, b=40),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    return milk_fig, methane_fig

# Executar o servidor
if __name__ == "__main__":
    app.run_server(debug=True)
