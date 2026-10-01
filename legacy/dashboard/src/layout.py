from dash import dcc, html

def create_layout():
    """Create the layout for the dashboard."""
    return html.Div([
        html.H1("Dairy Production Dashboard"),
        
        dcc.Dropdown(id='property-filter', multi=True, placeholder="Select Properties"),
        dcc.DatePickerRange(id='period-filter', start_date_placeholder_text="Start Period", end_date_placeholder_text="End Period"),

        html.Div([
            dcc.Graph(id='milk-production-chart'),
            dcc.Graph(id='carbon-emission-chart'),
        ], className='chart-container'),

        html.Div(id='indicators'),
    ])
