# Imports necessários
import dash
import pandas as pd
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

# Carregando os dados
df = pd.read_csv('/home/pedro_estudos/Documentos/GitHub/measuring-enteric-fermentation-emissions-application/dashboard/data/property_data.csv', sep=";")
df['Period'] = pd.to_datetime(df['Period'])
df['Year'] = df['Period'].dt.year
df['Month'] = df['Period'].dt.month

# Tema aprimorado para o layout
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])

# Dropdown para seleção de propriedade
property_dropdown = html.Div([
    dbc.Label("Select Property", html_for="property-dropdown", className="font-weight-bold"),
    dcc.Dropdown(
        id="property-dropdown",
        options=[{'label': prop, 'value': prop} for prop in df["Property"].unique()],
        value=df["Property"].unique()[0],
        multi=False,
        clearable=False,
        style={"font-weight": "bold"}
    ),
], className="mb-4")

# Dropdowns para seleção de ano e mês com estilo melhorado
period_dropdowns = html.Div([
    dbc.Label("Select Period Range", html_for="period-dropdown", className="font-weight-bold"),
    dbc.Row([
        dbc.Col(dcc.Dropdown(
            id='start-year',
            clearable=False,
            placeholder="Start Year",
            style={"font-weight": "bold"}
        )),
        dbc.Col(dcc.Dropdown(
            id='start-month',
            clearable=False,
            placeholder="Start Month",
            style={"font-weight": "bold"}
        )),
        dbc.Col(dcc.Dropdown(
            id='end-year',
            clearable=False,
            placeholder="End Year",
            style={"font-weight": "bold"}
        )),
        dbc.Col(dcc.Dropdown(
            id='end-month',
            clearable=False,
            placeholder="End Month",
            style={"font-weight": "bold"}
        )),
    ])
], className="mb-4")

# Botão de Previsões
forecast_button = dbc.Button("Generate Prediction", id="open-forecast-modal", color="primary", className="mb-4")

# Modal para solicitar melhorias no layout
forecast_modal = dbc.Modal(
    [
        dbc.ModalHeader("Generate Prediction"),
        dbc.ModalBody([
            dbc.Label("Descreva a melhoria desejada:"),
            dbc.Textarea(id="forecast-description", placeholder="Escreva aqui..."),
        ]),
        dbc.ModalFooter(
            dbc.Button("Enviar", id="submit-forecast", color="primary")
        ),
    ],
    id="forecast-modal",
    centered=True,
    is_open=False
)

# Layout principal
app.layout = dbc.Container([
    html.H1("Milk Production and Carbon Emissions Analysis", className="text-center mt-4 mb-4 display-4 font-weight-bold"),
    dbc.Row([
        dbc.Col([property_dropdown, period_dropdowns, forecast_button], md=3),
        dbc.Col(html.Div(id='kpi-cards'), md=9),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='line-chart'), md=6),
        dbc.Col(dcc.Graph(id='carbon-evolution-chart'), md=6),
    ], className="mb-4"),
    dbc.Row([
        dbc.Col(dcc.Graph(id='co2-per-liter-chart'), md=12),
    ]),
    forecast_modal
], fluid=True, style={"padding": "20px"})

# Callback para abrir/fechar o modal de previsões
@app.callback(
    Output("forecast-modal", "is_open"),
    [Input("open-forecast-modal", "n_clicks"), Input("submit-forecast", "n_clicks")],
    [dash.dependencies.State("forecast-modal", "is_open")]
)
def toggle_forecast_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# Callback para atualizar as opções de ano com base na propriedade selecionada
@app.callback(
    [Output('start-year', 'options'),
     Output('end-year', 'options'),
     Output('start-year', 'value'),
     Output('end-year', 'value')],
    [Input('property-dropdown', 'value')]
)
def update_year_options(selected_property):
    filtered_df = df[df['Property'] == selected_property]
    available_years = sorted(filtered_df['Year'].unique())
    year_options = [{'label': str(year), 'value': year} for year in available_years]
    
    default_start_year = available_years[0] if available_years else None
    default_end_year = available_years[-1] if available_years else None
    
    return year_options, year_options, default_start_year, default_end_year

# Callback para atualizar as opções de mês com base no ano selecionado
@app.callback(
    [Output('start-month', 'options'),
     Output('end-month', 'options'),
     Output('start-month', 'value'),
     Output('end-month', 'value')],
    [Input('property-dropdown', 'value'),
     Input('start-year', 'value'),
     Input('end-year', 'value')]
)
def update_month_options(selected_property, start_year, end_year):
    filtered_df = df[df['Property'] == selected_property]
    start_month_options, end_month_options = [], []
    default_start_month, default_end_month = None, None

    if start_year:
        start_months = sorted(filtered_df[filtered_df['Year'] == start_year]['Month'].unique())
        start_month_options = [{'label': str(month), 'value': month} for month in start_months]
        default_start_month = start_months[0] if start_months else None

    if end_year:
        end_months = sorted(filtered_df[filtered_df['Year'] == end_year]['Month'].unique())
        end_month_options = [{'label': str(month), 'value': month} for month in end_months]
        default_end_month = end_months[-1] if end_months else None

    return start_month_options, end_month_options, default_start_month, default_end_month

# Callback para atualizar os KPIs
@app.callback(
    Output('kpi-cards', 'children'),
    [Input('property-dropdown', 'value'),
     Input('start-year', 'value'),
     Input('start-month', 'value'),
     Input('end-year', 'value'),
     Input('end-month', 'value')]
)
def update_kpis(selected_property, start_year, start_month, end_year, end_month):
    if not all([start_year, start_month, end_year, end_month]):
        return []

    start_period = pd.to_datetime(f"{start_year}-{start_month:02d}")
    end_period = pd.to_datetime(f"{end_year}-{end_month:02d}")

    dff = df[(df['Property'] == selected_property) & (df['Period'] >= start_period) & (df['Period'] <= end_period)]

    total_milk_production = dff['Milk_Production'].sum()
    total_carbon_emissions = dff['enteric_tCO2e'].sum()
    carbon_per_liter = total_carbon_emissions / total_milk_production if total_milk_production else 0
    carbon_per_area = total_carbon_emissions / dff['Area_Used_for_Dairy_Activity'].sum() if dff['Area_Used_for_Dairy_Activity'].sum() else 0
    milk_per_area = total_milk_production / dff['Area_Used_for_Dairy_Activity'].sum() if dff['Area_Used_for_Dairy_Activity'].sum() else 0

    return dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Total Milk Production", className="font-weight-bold"),
            dbc.CardBody(f"{total_milk_production:.2f} liters", className="display-6 font-weight-bold")
        ], className="shadow-sm", style={"margin-bottom": "10px", "background-color": "#f8f9fa"})),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Total CO2 Emissions", className="font-weight-bold"),
            dbc.CardBody(f"{total_carbon_emissions:.2f} tCO2e", className="display-6 font-weight-bold")
        ], className="shadow-sm", style={"margin-bottom": "10px", "background-color": "#f8f9fa"})),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Kg of CO2 per Liter of Milk", className="font-weight-bold"),
            dbc.CardBody(f"{carbon_per_liter:.4f} kgCO2e/L", className="display-6 font-weight-bold")
        ], className="shadow-sm", style={"margin-bottom": "10px", "background-color": "#f8f9fa"})),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Kg of CO2 per Area Used", className="font-weight-bold"),
            dbc.CardBody(f"{carbon_per_area:.4f} kgCO2e/ha", className="display-6 font-weight-bold")
        ], className="shadow-sm", style={"margin-bottom": "10px", "background-color": "#f8f9fa"})),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Liters of Milk per Area Used", className="font-weight-bold"),
            dbc.CardBody(f"{milk_per_area:.2f} L/ha", className="display-6 font-weight-bold")
        ], className="shadow-sm", style={"margin-bottom": "10px", "background-color": "#f8f9fa"})),
    ], className="g-4")

# Callback para atualizar o gráfico de produção de leite
@app.callback(
    Output('line-chart', 'figure'),
    [Input('property-dropdown', 'value'),
     Input('start-year', 'value'),
     Input('start-month', 'value'),
     Input('end-year', 'value'),
     Input('end-month', 'value')]
)
def update_line_chart(selected_property, start_year, start_month, end_year, end_month):
    if not all([start_year, start_month, end_year, end_month]):
        return go.Figure()

    start_date = pd.to_datetime(f"{start_year}-{start_month:02d}")
    end_date = pd.to_datetime(f"{end_year}-{end_month:02d}")

    dff = df[(df['Property'] == selected_property) & (df['Period'] >= start_date) & (df['Period'] <= end_date)]
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=dff['Period'], y=dff['Milk_Production'], mode='lines+markers', name=selected_property))

    fig.update_layout(
        title="<b>Milk Production Over Time</b>",
        title_x=0.5,
        xaxis_title="<b>Period</b>",
        yaxis_title="<b>Milk Production (liters)</b>",
        font=dict(family="Arial", size=14, color="black"),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            tickangle=-45, 
            showgrid=True, 
            gridcolor='LightGray',
            tickfont=dict(color="black"),
            titlefont=dict(color="black")
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor='LightGray',
            tickfont=dict(color="black"),
            titlefont=dict(color="black")
        )
    )
    return fig

# Callback para atualizar o gráfico de emissões de carbono
@app.callback(
    Output('carbon-evolution-chart', 'figure'),
    [Input('property-dropdown', 'value'),
     Input('start-year', 'value'),
     Input('start-month', 'value'),
     Input('end-year', 'value'),
     Input('end-month', 'value')]
)
def update_carbon_evolution_chart(selected_property, start_year, start_month, end_year, end_month):
    if not all([start_year, start_month, end_year, end_month]):
        return go.Figure()

    start_date = pd.to_datetime(f"{start_year}-{start_month:02d}")
    end_date = pd.to_datetime(f"{end_year}-{end_month:02d}")

    dff = df[(df['Property'] == selected_property) & (df['Period'] >= start_date) & (df['Period'] <= end_date)]
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=dff['Period'], y=dff['enteric_tCO2e'], mode='lines+markers', name=selected_property))

    fig.update_layout(
        title="<b>Carbon Emissions Over Time</b>",
        title_x=0.5,
        xaxis_title="<b>Period</b>",
        yaxis_title="<b>CO2 Emissions (tCO2e)</b>",
        font=dict(family="Arial", size=14, color="black"),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            tickangle=-45, 
            showgrid=True, 
            gridcolor='LightGray',
            tickfont=dict(color="black"),
            titlefont=dict(color="black")
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor='LightGray',
            tickfont=dict(color="black"),
            titlefont=dict(color="black")
        )
    )
    return fig

# Callback para atualizar o gráfico de CO2 por litro de leite
@app.callback(
    Output('co2-per-liter-chart', 'figure'),
    [Input('property-dropdown', 'value'),
     Input('start-year', 'value'),
     Input('start-month', 'value'),
     Input('end-year', 'value'),
     Input('end-month', 'value')]
)
def update_co2_per_liter_chart(selected_property, start_year, start_month, end_year, end_month):
    if not all([start_year, start_month, end_year, end_month]):
        return go.Figure()

    start_date = pd.to_datetime(f"{start_year}-{start_month:02d}")
    end_date = pd.to_datetime(f"{end_year}-{end_month:02d}")

    dff = df[(df['Property'] == selected_property) & (df['Period'] >= start_date) & (df['Period'] <= end_date)]
    dff['CO2_per_Liter'] = dff['enteric_tCO2e'] / dff['Milk_Production']

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dff['Period'], 
        y=dff['CO2_per_Liter'], 
        mode='lines+markers', 
        name=selected_property
    ))

    fig.update_layout(
        title="<b>Kg of CO2 per Liter of Milk Over Time</b>",
        title_x=0.5,
        xaxis_title="<b>Period</b>",
        yaxis_title="<b>CO2 per Liter (kgCO2e/L)</b>",
        font=dict(family="Arial", size=14, color="black"),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            tickangle=-45, 
            showgrid=True, 
            gridcolor='LightGray',
            tickfont=dict(color="black"),
            titlefont=dict(color="black")
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor='LightGray',
            tickfont=dict(color="black"),
            titlefont=dict(color="black")
        )
    )

    return fig

# Callback para o gráfico de previsões
# @app.callback(
#     Output('forecast-graph', 'figure'),
#     [Input('property-dropdown', 'value'),
#      Input('start-year', 'value'),
#      Input('start-month', 'value'),
#      Input('end-year', 'value'),
#      Input('end-month', 'value')]
# )
# def update_forecast_graph(selected_property, start_year, start_month, end_year, end_month):
#     if not all([start_year, start_month, end_year, end_month]):
#         return go.Figure()

#     # Exemplo de como os dados de previsão podem ser obtidos e plotados
#     actual_periods = pd.date_range(start=f"{start_year}-{start_month:02d}", end=f"{end_year}-{end_month:02d}", freq='M')
#     actual_methane = [100 + i * 10 for i in range(len(actual_periods))]
#     forecast_periods = pd.date_range(start=f"{end_year}-{end_month:02d}", periods=12, freq='M')
#     predictions_methane = [actual_methane[-1] * 1.05**i for i in range(12)]
    
#     colors = ["#FF5733", "#33FF57"]

#     methane_fig = go.Figure()
#     methane_fig.add_trace(go.Bar(
#         x=actual_periods, 
#         y=actual_methane, 
#         name="Real Methane Emissions", 
#         marker_color=colors[0],
#         opacity=0.8
#     ))
#     methane_fig.add_trace(go.Bar(
#         x=forecast_periods, 
#         y=predictions_methane, 
#         name="Methane Emissions Forecast", 
#         marker_color=colors[1],
#         opacity=0.7
#     ))
#     methane_fig.update_layout(
#         title=f"<b>Methane Emissions - {selected_property}</b>",
#         title_x=0.5,
#         xaxis_title="<b>Period</b>",
#         yaxis_title="<b>tCO2e</b>",
#         barmode='group',
#         font=dict(size=14, color="black", family="Arial"),
#         legend=dict(
#             title="<b>Legend</b>",
#             orientation="h",  
#             yanchor="bottom",
#             y=1.02,
#             xanchor="center",
#             x=0.5,
#             font=dict(size=12)
#         ),
#         xaxis=dict(tickangle=-45, showgrid=True, gridcolor='LightGray'),
#         yaxis=dict(showgrid=True, gridcolor='LightGray'),
#         margin=dict(l=40, r=40, t=60, b=40),
#         plot_bgcolor='white',
#         paper_bgcolor='white'
#     )
#     return methane_fig

# Executando o app
if __name__ == "__main__":
    app.run_server(debug=True)
