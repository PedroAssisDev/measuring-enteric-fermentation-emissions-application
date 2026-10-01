import pandas as pd

def calcular_emissoes_baseline(EF_enteric, GWP):
    """
    Calcula as emissões de metano (CH₄) de fermentação entérica em um cenário de linha de base.

    Parâmetros:
    EF_enteric:  representa os fatores de emissão de metano (kg CH₄)
                                para cada grupo de animais em uma fazenda.
    GWP (float): Potencial de aquecimento global do metano (GWP).

    Retorna:
    float: Emissões totais de metano em equivalentes de CO2 (tCO2e).
    """
    
    # Conversão para toneladas de CO2 equivalente
    BEE_enteric_tCO2e = (EF_enteric * GWP) / 1000
    
    return BEE_enteric_tCO2e

def calcular_ef_enteric(EFProduction, Ni, Daysi):
    """
    Calcula o fator de emissão entérica (EFEnteric) para um grupo de animais durante o período de monitoramento.

    Parâmetros:
    EFProduction (float): Fator de produção de emissões entéricas médio para o grupo de animais (kg CH4 cabeça-1 d-1).
    Ni (int): Número médio de animais no grupo durante o período de monitoramento (cabeças).
    Daysi (int): Número de dias que cada animal no grupo passou na fazenda durante o período de monitoramento (dias).

    Retorna:
    float: Fator de emissão entérica para o grupo de animais (kg CH4).
    """
    EFEnteric = EFProduction * Ni * Daysi
    return EFEnteric


def load_data(filepath):
    """
    Carrega o dataset a partir de um arquivo CSV.
    
    :param filepath: Caminho para o arquivo CSV.
    :return: DataFrame pandas com os dados carregados.
    """
    dairy_cattle = 87
    other_cattle = 56
    GWP = 28.00    
    DAYS_IN_PERIOD = 30

    try:
        data = pd.read_csv(filepath, sep=";", parse_dates=True)
        data.columns = data.columns.str.strip()  # Remove espaços em branco
    except Exception as e:
        print(f"Erro ao carregar o arquivo: {e}")
        return None

    for index, row in data.iterrows():
        count = row[["Dry_Cows", "Pregnant_Heifers", "Heifers_in_Raising", 
                      "Suckling_Calves_female", "Suckling_Calves_male", 
                      "Male_Calves_in_Raising", "Male_Calves_in_Fattening", 
                      "Draft_and_Breeding_Bulls", "Equines_and_Mules"]].sum()
        
        ef_enteric_kgCH4 = (
            calcular_ef_enteric(dairy_cattle, row['Number_of_Lactating_Cows'], DAYS_IN_PERIOD) +
            calcular_ef_enteric(other_cattle, count, DAYS_IN_PERIOD)
        )
        
        enteric_tCO2e = calcular_emissoes_baseline(ef_enteric_kgCH4, GWP)
        data.loc[index, "Number_of_Dry_Cows"] = count
        data.loc[index, "ef_enteric_kgCH4"] = ef_enteric_kgCH4
        data.loc[index, "enteric_tCO2e"] = enteric_tCO2e
        
    return data
