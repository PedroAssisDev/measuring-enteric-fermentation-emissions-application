from dash import Dash
from src.layout import create_layout
from src.callbacks import register_callbacks

# Inicializa a aplicação Dash
app = Dash(__name__)

# Configura o layout da aplicação
app.layout = create_layout()

# Registra os callbacks
register_callbacks(app)

# Executa o servidor
if __name__ == '__main__':
    app.run_server(debug=True)
