import pandas as pd
from owlready2 import *
from datetime import datetime
from create_ontology import generate_ontology

current_directory = os.path.dirname(os.path.abspath(__file__))
base_directory = os.path.dirname(current_directory)
ontology_directory = os.path.join(base_directory, "ontology/owl_files")
data_file = os.path.join(base_directory, "data/data_standardized/property_data_standardized.csv")
file_ontology_1 = os.path.join(ontology_directory, "EntericMeasureOnto.owl")
file_ontology_2 = os.path.join(ontology_directory, "final_populated_EntericMeasureOnto.owl")
file_ontology_3 = os.path.join(ontology_directory, "synced_reasoner_EntericMeasureOnto.owl")

def populate_ontology_from_csv(csv_path):
    """Populates the ontology with data from a CSV file."""
    if os.path.isfile(file_ontology_1):
        onto = get_ontology(file_ontology_1)
        onto.load()
    else:
        generate_ontology(True)
        onto = get_ontology(file_ontology_1)
        onto.load()
        
    data = pd.read_csv(csv_path, sep=";")
    GWP = 28.00
    EMISSION_FACTOR_TIER_1_DAIRY_CATTLE = 87.00
    EMISSION_FACTOR_TIER_1_OTHER_CATTLE = 56.00
    with onto:
        for _, record in data.iterrows():
            
            property_name = record['Property']
            if not onto.search(iri=f"*{property_name}_Property"):
                prop = onto.RuralProperty(f"{property_name}_Property")
                prop.propertyName.append(property_name)
                
                # Adicionando propriedades específicas
                prop.gwp.append(GWP)
                
                # Criar instância de BaseLineEmissionsTier1 e adicionar propriedades
                basileneTier1 = onto.BaseLineEmissionsTier1(f"{property_name}_BaseLineEmissionsTier1")
                basileneTier1.emissionFactorDairyCattleTier1.append(EMISSION_FACTOR_TIER_1_DAIRY_CATTLE)
                basileneTier1.emissionFactorOtherCattleTier1.append(EMISSION_FACTOR_TIER_1_OTHER_CATTLE)
                
                # Relacionar a propriedade rural com BaseLineEmissionsTier1
                prop.HasBaseLineEmissions.append(basileneTier1)
            else:
                prop = onto.search(iri=f"*{property_name}_Property")[0]
            
            # Adicionar produção de leite mensal
            monthly_production = onto.MonthlyProduction(f"{property_name}_MonthlyProduction_{record['Period']}")
            monthly_production.measurementDate.append(datetime.strptime(record['Period'], "%Y-%m-%d"))
            monthly_production.milkProduction.append(float(record['Milk_Production']))
            monthly_production.milkSales.append(float(record['Milk_Sales']))
            #monthly_production.timeGranularity.append(onto.Monthly())
            
            # Relacionar produção com a propriedade
            prop.HasMonthlyProduction.append(monthly_production)
            
            # Adicionar preço bruto do leite
            prop.milkGrossPrice.append(float(record['Milk_Gross_Price']))
            
            # Adicionar número de vacas lactantes
            prop.monthlyDairyCattleTotal.append(int(record['Number_of_Lactating_Cows']))
            
            # Adicionar número de empregados durante o mês
            prop.employeesDuringTheMonth.append(int(record['Employees_During_the_Month']))
            
            # Adicionar área usada para atividade leiteira
            prop.propertySizeForDairyActivity.append(float(record['Area_Used_for_Dairy_Activity']))
            
            # Adicionar outros dados de gado
            prop.monthlyOtherCattleTotal.append(float(record[["Dry_Cows",
                                                            "Pregnant_Heifers",
                                                            "Heifers_in_Raising",
                                                            "Suckling_Calves_female",
                                                            "Suckling_Calves_male",
                                                            "Male_Calves_in_Raising",
                                                            "Male_Calves_in_Fattening",
                                                            "Draft_and_Breeding_Bulls",
                                                            "Equines_and_Mules"]].sum())
                                                )
        onto.save(file_ontology_2)
        try:
            sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)
            onto.save(file=file_ontology_3, format="rdfxml")
        except Exception as e:
            print(f"Erro durante a inferência: {e}")
        


# Exemplo de uso da função

# Carregar ou criar a ontologia
# Popular a ontologia com os dados do CSV
populate_ontology_from_csv(data_file)
