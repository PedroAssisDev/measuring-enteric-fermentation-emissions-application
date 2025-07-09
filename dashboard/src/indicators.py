def calculate_indicators(df):
    """Calculate key performance indicators for the dashboard."""
    total_milk_production = df['Milk_Production'].sum()
    total_carbon_emission = df['enteric_tCO2e'].sum()
    carbon_per_liter = total_carbon_emission / total_milk_production
    carbon_per_area = total_carbon_emission / df['Area_Used_for_Dairy_Activity'].sum()
    carbon_per_cow = total_carbon_emission / df['Number_of_Lactating_Cows'].sum()
    milk_per_area = total_milk_production / df['Area_Used_for_Dairy_Activity'].sum()
    milk_per_cow = total_milk_production / df['Number_of_Lactating_Cows'].sum()
    
    return [
        f"Total Milk Production: {total_milk_production:.2f} liters",
        f"Total CO2 Emissions: {total_carbon_emission:.2f} tCO2e",
        f"CO2 per Liter of Milk: {carbon_per_liter:.2f} kgCO2e",
        f"CO2 per Area: {carbon_per_area:.2f} kgCO2e/ha",
        f"CO2 per Lactating Cow: {carbon_per_cow:.2f} kgCO2e/cow",
        f"Milk per Area: {milk_per_area:.2f} liters/ha",
        f"Milk per Lactating Cow: {milk_per_cow:.2f} liters/cow"
    ]
