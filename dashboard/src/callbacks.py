from dash import Input, Output
from .data_preparation import load_data, clean_data
from .indicators import calculate_indicators

def register_callbacks(app):
    @app.callback(
        [Output('milk-production-chart', 'figure'),
         Output('carbon-emission-chart', 'figure'),
         Output('indicators', 'children')],
        [Input('property-filter', 'value'),
         Input('period-filter', 'start_date'),
         Input('period-filter', 'end_date')]
    )
    def update_charts(selected_properties, start_date, end_date):
        data = load_data('dashboard/data/property_data.csv')
        data = clean_data(data)

        if selected_properties:
            data = data[data['Property'].isin(selected_properties)]
        if start_date and end_date:
            data = data[(data['Period'] >= start_date) & (data['Period'] <= end_date)]

        indicators = calculate_indicators(data)
        
        # Criação dos gráficos aqui (usando Plotly)
        milk_production_chart = ...
        carbon_emission_chart = ...

        return milk_production_chart, carbon_emission_chart, indicators
