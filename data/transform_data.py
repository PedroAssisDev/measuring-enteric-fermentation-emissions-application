import pandas as pd
from pydantic import BaseModel, field_validator, ValidationError
import os

# Definir a classe para validar os dados
class DairyData(BaseModel):
    Property: str
    Period: int
    Milk_Production: float
    Milk_Sales: float
    Milk_Gross_Price: float
    Number_of_Lactating_Cows: float
    Employees_During_the_Month: float
    Area_Used_for_Dairy_Activity: float
    Reproducers: float
    Lactating_Cows: float
    Dry_Cows: float
    Pregnant_Heifers: float
    Heifers_in_Raising: float
    Suckling_Calves_female: float
    Suckling_Calves_male: float
    Male_Calves_in_Raising: float
    Male_Calves_in_Fattening: float
    Draft_and_Breeding_Bulls: float
    Equines_and_Mules: float

    @field_validator('Period')
    def period_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Period must be a positive integer')
        return v

    @field_validator('Milk_Production', 'Milk_Sales', 'Milk_Gross_Price', 'Area_Used_for_Dairy_Activity')
    def value_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError('Value must be non-negative')
        return v

    @field_validator('Number_of_Lactating_Cows', 'Employees_During_the_Month', 'Reproducers', 'Lactating_Cows', 'Dry_Cows', 'Pregnant_Heifers', 'Heifers_in_Raising', 'Suckling_Calves_female', 'Suckling_Calves_male', 'Male_Calves_in_Raising', 'Male_Calves_in_Fattening', 'Draft_and_Breeding_Bulls', 'Equines_and_Mules')
    def count_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError('Count must be non-negative')
        return v

# Função para validar os dados do DataFrame
def validate_row(row):
    try:
        DairyData(
            Property=row["Property"],
            Period= row["Period"],
            Milk_Production=row["Milk Production (liters/month)"],
            Milk_Sales=row["Milk Sales (liters/month)"],
            Milk_Gross_Price=row["Milk Gross Price (R$/liter)"],
            Number_of_Lactating_Cows=row["Number of Lactating Cows"],
            Employees_During_the_Month=row["Employees During the Month (man-days/month)"],
            Area_Used_for_Dairy_Activity=row["Area Used for Dairy Activity (ha)"],
            Reproducers=row["Reproducers"],
            Lactating_Cows=row["Lactating Cows"],
            Dry_Cows=row["Dry Cows"],
            Pregnant_Heifers=row["Pregnant Heifers"],
            Heifers_in_Raising=row["Heifers in Raising"],
            Suckling_Calves_female=row["Suckling Calves (female)"],
            Suckling_Calves_male=row["Suckling Calves (male)"],
            Male_Calves_in_Raising=row["Male Calves in Raising"],
            Male_Calves_in_Fattening=row["Male Calves in Fattening"],
            Draft_and_Breeding_Bulls=row["Draft and Breeding Bulls"],
            Equines_and_Mules=row["Equines and Mules"]
        )
        return True
    except ValidationError as e:
        print(f"Error in row {row.name}: {e}")
        return False

def adjust_period(row):
    final_period = pd.Timestamp('2023-01-01')
    row = (final_period - pd.DateOffset(months=row)).strftime('%Y-%m-%d')
    return row

# Validar todas as linhas do DataFrame
current_directory = os.path.dirname(os.path.abspath(__file__))
base_directory = os.path.dirname(os.path.join(current_directory,"data"))
data_orig_directory = os.path.join(base_directory, "data_orig/Property_data_orig.tsv")

data = pd.read_csv(data_orig_directory, sep=";")


# Criar DataFrame
df = pd.DataFrame(data)
valid_rows = df.apply(validate_row, axis=1)
valid_data = df[valid_rows]

# Ajustar o período
df['Period'] = df['Period'].apply(lambda x: adjust_period(x))

df.columns = [
"Property",
"Period",
"Milk_Production",
"Milk_Sales",
"Milk_Gross_Price",
"Number_of_Lactating_Cows",
"Employees_During_the_Month",
"Area_Used_for_Dairy_Activity",
"Reproducers",
"Lactating_Cows",
"Dry_Cows",
"Pregnant_Heifers",
"Heifers_in_Raising",
"Suckling_Calves_female",
"Suckling_Calves_male",
"Male_Calves_in_Raising",
"Male_Calves_in_Fattening",
"Draft_and_Breeding_Bulls",
"Equines_and_Mules"
]
# Mostrar os dados válidos
data_standardized_directory = os.path.join(base_directory, "data_standardized/property_data_standardized.csv")
df.to_csv(data_standardized_directory, sep=";", index=False)
print(df)
