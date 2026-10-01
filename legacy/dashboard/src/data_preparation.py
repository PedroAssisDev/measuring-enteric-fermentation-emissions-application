import pandas as pd

def load_data(filepath):
    """Load data from a CSV file."""
    return pd.read_csv(filepath, sep= ";")

def clean_data(df):
    """Clean and preprocess the data."""
    # Implementar a limpeza e transformação dos dados conforme necessário
    df['Period'] = pd.to_datetime(df['Period'])
    return df
