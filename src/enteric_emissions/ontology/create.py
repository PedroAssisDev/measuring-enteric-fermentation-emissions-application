"""EntericMeasureOnto TBox definition (classes, properties, SWRL rules).

Scientific structure is preserved from the research implementation.
Engineering changes are limited to portable path resolution.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from owlready2 import (
    DataProperty,
    FunctionalProperty,
    Imp,
    ObjectProperty,
    SymmetricProperty,
    Thing,
    get_ontology,
    onto_path,
)

from enteric_emissions.config import get_paths

logger = logging.getLogger(__name__)


def generate_ontology(save: bool = True, output_path: Path | None = None):
    """Generate the ontology with defined classes, properties, and rules."""
    paths = get_paths()
    file_ontology_1 = str(output_path or paths.ontology_tbox)
    Path(file_ontology_1).parent.mkdir(parents=True, exist_ok=True)

    # Preserve original Owlready2 loading convention (literal ontology name).
    onto_path.append(file_ontology_1)
    onto = get_ontology("http://carbonseco.org/enteric_measure_onto.owl")
    with onto:
        define_classes_and_properties(onto)
        create_rules(onto)

    if save:
        onto.save(file_ontology_1)
        logger.info("Saved EntericMeasureOnto TBox to %s", file_ontology_1)
    return onto

def define_classes_and_properties(onto):
    """Defines classes and properties for the ontology."""
    with onto:
        # Definição de classes principais
        
        # Classe para representar o gado
        class Cattle(Thing):
            """Classe que representa o gado."""
            pass

        # Subclasses de Cattle
        class DairyCattle(Cattle):
            """Gado leiteiro."""
            pass

        class OtherCattle(Cattle):
            """Outros tipos de gado."""
            pass

        # Classe para representar propriedades rurais
        class RuralProperty(Thing):
            """Propriedade rural."""
            pass

        # Classe para dados de medição
        class MeasurementData(Thing):
            """Dados de medição."""
            pass

        # Subclasses de MeasurementData
        class GeneralMeasurementData(MeasurementData):
            """Dados de medição gerais."""
            pass

        class CattleMeasurementData(MeasurementData):
            """Dados de medição de gado."""
            pass

        # Classe para representar emissões base line
        class BaseLineEmissions(Thing):
            """Emissões base line."""
            pass
        
        # Subclasses de BaseLineEmissions
        class BaseLineEmissionsTier1(BaseLineEmissions):
            """Emissões base line Tier 1."""
            pass
        
        class BaseLineEmissionsTier2(BaseLineEmissions):
            """Emissões base line Tier 2."""
            pass
        
        # Classe para granularidade de tempo
        class TimeGranularity(Thing):
            """Granularidade de tempo."""
            pass
        
        # Subclasses de TimeGranularity
        class Daily(TimeGranularity):
            """Granularidade diária."""
            pass
        
        class Monthly(TimeGranularity):
            """Granularidade mensal."""
            pass
        
        class Yearly(TimeGranularity):
            """Granularidade anual."""
            pass

        # Classe para dados de produção
        class ProductionData(Thing):
            """Dados de produção."""
            pass
        
        # Subclasses de ProductionData
        class DailyProduction(ProductionData):
            """Produção diária."""
            pass
        
        class MonthlyProduction(ProductionData):
            """Produção mensal."""
            pass
        
        class YearlyProduction(ProductionData):
            """Produção anual."""
            pass

        # Definição de propriedades de dados

        # Propriedades de identificação e nomes
        class cattleName(DataProperty):
            """Nome do gado."""
            domain = [Cattle, OtherCattle, CattleMeasurementData]
            range = [str]
        
        class cattleId(DataProperty):
            """ID do gado."""
            domain = [Cattle, OtherCattle, CattleMeasurementData]
            range = [str]
        
        # Propriedades de medição
        class weight(DataProperty):
            """Peso do gado."""
            domain = [Cattle, OtherCattle, CattleMeasurementData]
            range = [float]
        
        class milkProduction(DataProperty):
            """Produção de leite."""
            domain = [DairyCattle, CattleMeasurementData, RuralProperty, ProductionData]
            range = [float]
            
        class milkSales(DataProperty):
            """Produção de leite."""
            domain = [DairyCattle, CattleMeasurementData, RuralProperty, ProductionData]
            range = [float]
        
        class measurementDate(DataProperty):
            """Data da medição."""
            domain = [MeasurementData, ProductionData]
            range = [datetime]
        
        # Propriedades de fator de emissão
        class emissionFactorDairyCattleTier1(DataProperty):
            """Fator de emissão Tier 1."""
            domain = [DairyCattle, CattleMeasurementData, RuralProperty, BaseLineEmissions]
            range = [float]
            
        class emissionFactorOtherCattleTier1(DataProperty):
            """Fator de emissão Tier 1."""
            domain = [OtherCattle, CattleMeasurementData, RuralProperty, BaseLineEmissions]
            range = [float]
        
        class emissionFactorTier2(DataProperty):
            """Fator de emissão Tier 2."""
            domain = [Cattle, CattleMeasurementData, RuralProperty, BaseLineEmissions]
            range = [float]
        
        # Propriedades de densidade e ingestão
        class energyDensity(DataProperty):
            """Densidade energética."""
            domain = [Cattle, CattleMeasurementData]
            range = [float]
        
        class dryMatterIntake(DataProperty):
            """Ingestão de matéria seca."""
            domain = [Cattle, CattleMeasurementData]
            range = [float]
        
        # Propriedades de granularidade de tempo
        class timeGranularity(DataProperty):
            """Granularidade de tempo."""
            domain = [MeasurementData]
            range = [TimeGranularity]
        
        # Propriedades de tempo no campo
        class monthsOnFarm(DataProperty):
            """Meses no campo."""
            domain = [Cattle, OtherCattle]
            range = [float]
        
        class daysOnFarm(DataProperty):
            """Dias no campo."""
            domain = [Cattle, OtherCattle]
            range = [float]
        
        # Propriedades de emissões individuais
        class individualEntericEmissionFactorTier1(DataProperty):
            """Fator de emissão entérica individual Tier 1."""
            domain = [Cattle]
            range = [float]
        
        class individualEntericEmissionTier1(DataProperty):
            """Emissão entérica individual Tier 1."""
            domain = [Cattle]
            range = [float]
        
        class individualEntericEmissionFactorTier2(DataProperty):
            """Fator de emissão entérica individual Tier 2."""
            domain = [Cattle]
            range = [float]
        
        class individualEntericEmissionTier2(DataProperty):
            """Emissão entérica individual Tier 2."""
            domain = [Cattle]
            range = [float]
        
        # Propriedades de quantidade e produção
        class animalQuantity(DataProperty):
            """Quantidade de animais."""
            domain = [RuralProperty]
            range = [float]
        
        class totalMilkProduction(DataProperty):
            """Produção total de leite."""
            domain = [RuralProperty, GeneralMeasurementData, ProductionData]
            range = [float]
        
        # Propriedades de GWP e nome da propriedade
        class gwp(DataProperty):
            """Potencial de aquecimento global."""
            domain = [Cattle, RuralProperty]
            range = [float]
        
        class propertyName(DataProperty):
            """Nome da propriedade."""
            domain = [RuralProperty]
            range = [str]
        
        # Propriedades de emissões totais
        class totalEmissionsTier1(DataProperty):
            """Emissões totais Tier 1."""
            domain = [RuralProperty, BaseLineEmissions, Cattle, GeneralMeasurementData, ProductionData]
            range = [float]
        
        class totalEmissionsTier2(DataProperty):
            """Emissões totais Tier 2."""
            domain = [RuralProperty, BaseLineEmissions, Cattle, GeneralMeasurementData, ProductionData]
            range = [float]
        
        # Propriedades de ingestão de energia
        class grossEnergyIntake(DataProperty):
            """Ingestão de energia bruta."""
            domain = [Cattle]
            range = [float]
        
        # Propriedades de fator de emissão entérica
        class totalEntericEmissionFactorTier1(DataProperty):
            """Fator de emissão entérica total Tier 1."""
            domain = [BaseLineEmissionsTier1]
            range = [float]
        
        class dailyEntericEmissionFactorTier1(DataProperty):
            """Fator de emissão entérica diária Tier 1."""
            domain = [BaseLineEmissionsTier1]
            range = [float]

        class monthlyEntericEmissionFactorTier1(DataProperty):
            """Fator de emissão entérica mensal Tier 1."""
            domain = [BaseLineEmissionsTier1]
            range = [float]

        class EntericEmissionFactorTier1(DataProperty):
            """Fator de emissão entérica Tier 1."""
            domain = [BaseLineEmissionsTier1]
            range = [float]
        
        class totalEntericEmissionFactorTier1(DataProperty):
            """Fator de emissão entérica total Tier 1."""
            domain = [BaseLineEmissionsTier1]
            range = [float]
        
        class dailyEntericEmissionFactorTier2(DataProperty):
            """Fator de emissão entérica diária Tier 2."""
            domain = [BaseLineEmissionsTier2]
            range = [float]

        class monthlyEntericEmissionFactorTier2(DataProperty):
            """Fator de emissão entérica mensal Tier 2."""
            domain = [BaseLineEmissionsTier2]
            range = [float]

        class EntericEmissionFactorTier2(DataProperty):
            """Fator de emissão entérica Tier 2."""
            domain = [BaseLineEmissionsTier2]
            range = [float]
        
        # Propriedade de tamanho da propriedade
        class propertySizeForDairyActivity(DataProperty):
            """Tamanho da propriedade."""
            domain = [RuralProperty]
            range = [float]        

        # Propriedades de produção de leite
        class dailyMilkProductionAverage(DataProperty):
            """Média diária de produção de leite."""
            domain = [RuralProperty]
            range = [float]

        class monthlyMilkProductionAverage(DataProperty):
            """Média mensal de produção de leite."""
            domain = [RuralProperty]
            range = [float]

        class yearlyMilkProductionAverage(DataProperty):
            """Média anual de produção de leite."""
            domain = [RuralProperty]
            range = [float]

        class dailyMilkProductionTotal(DataProperty):
            """Total diário de produção de leite."""
            domain = [RuralProperty]
            range = [float]

        class monthlyMilkProductionTotal(DataProperty):
            """Total mensal de produção de leite."""
            domain = [RuralProperty]
            range = [float]

        class yearlyMilkProductionTotal(DataProperty):
            """Total anual de produção de leite."""
            domain = [RuralProperty]
            range = [float]

        # Propriedades de gado por período
        class dailyDairyCattleAverage(DataProperty):
            """Média diária de gado."""
            domain = [RuralProperty]
            range = [float]

        class monthlyDairyCattleAverage(DataProperty):
            """Média mensal de gado."""
            domain = [RuralProperty]
            range = [float]

        class yearlyDairyCattleAverage(DataProperty):
            """Média anual de gado."""
            domain = [RuralProperty]
            range = [float]

        class dailyDairyCattleTotal(DataProperty):
            """Total diário de gado."""
            domain = [RuralProperty]
            range = [float]

        class monthlyDairyCattleTotal(DataProperty):
            """Total mensal de gado."""
            domain = [RuralProperty]
            range = [float]

        class yearlyDairyCattleTotal(DataProperty):
            """Total anual de gado."""
            domain = [RuralProperty]
            range = [float]
        
        # Propriedades de outros tipos de gado
        class dailyOtherCattleAverage(DataProperty):
            """Média diária de outros tipos de gado."""
            domain = [RuralProperty]
            range = [float]

        class monthlyOtherCattleAverage(DataProperty):
            """Média mensal de outros tipos de gado."""
            domain = [RuralProperty]
            range = [float]

        class yearlyOtherCattleAverage(DataProperty):
            """Média anual de outros tipos de gado."""
            domain = [RuralProperty]
            range = [float]

        class dailyOtherCattleTotal(DataProperty):
            """Total diário de outros tipos de gado."""
            domain = [RuralProperty]
            range = [float]

        class monthlyOtherCattleTotal(DataProperty):
            """Total mensal de outros tipos de gado."""
            domain = [RuralProperty]
            range = [float]

        class yearlyOtherCattleTotal(DataProperty):
            """Total anual de outros tipos de gado."""
            domain = [RuralProperty]
            range = [float]
        
        class milkGrossPrice(DataProperty):
            """Preço bruto do leite."""
            domain = [RuralProperty]
            range = [float]
        
        class employeesDuringTheMonth(DataProperty):
            """Número de empregados durante o mês."""
            domain = [RuralProperty]
            range = [int]

        # Definição de propriedades de objeto

        # Propriedades de medição
        class HasMeasurementData(ObjectProperty):
            """Relaciona gado com dados de medição."""
            domain = [Cattle]
            range = [CattleMeasurementData]

        # Propriedades de associação a propriedades rurais
        class BelongsToProperty(ObjectProperty, SymmetricProperty):
            """Relaciona gado a propriedades rurais."""
            domain = [Cattle]
            range = [RuralProperty]
        
        class HasCattleGroup(ObjectProperty):
            """Relaciona propriedades rurais com grupos de gado."""
            inverse_property = BelongsToProperty
            domain = [RuralProperty]
            range = [Cattle]
        
        class HasTotalEmissions(ObjectProperty, FunctionalProperty):
            """Relaciona emissões totais a propriedades rurais."""
            domain = [BaseLineEmissions]
            range = [RuralProperty]
        
        class HasGroupEmissions(ObjectProperty, FunctionalProperty):
            """Relaciona emissões de grupos a propriedades rurais."""
            domain = [RuralProperty]
            range = [Cattle]
        
        class HasAnimalQuantity(ObjectProperty, FunctionalProperty):
            """Relaciona quantidade de animais a propriedades rurais."""
            domain = [RuralProperty]
            range = [Cattle]
        
        class HasMilkProduction(ObjectProperty, FunctionalProperty):
            """Relaciona produção de leite a gado leiteiro."""
            domain = [RuralProperty]
            range = [DairyCattle]
        
        class HasBaseLineEmissions(ObjectProperty, SymmetricProperty):
            """Relaciona emissões base line a propriedades rurais."""
            domain = [RuralProperty]
            range = [BaseLineEmissions]

        class HasGeneralMeasurementData(ObjectProperty):
            """Relaciona propriedades rurais com dados de medição gerais."""
            domain = [RuralProperty]
            range = [GeneralMeasurementData]
        
        class HasCattleMeasurementData(ObjectProperty):
            """Relaciona gado com dados de medição específicos."""
            domain = [Cattle]
            range = [CattleMeasurementData]

        class HasDailyProduction(ObjectProperty):
            """Relaciona propriedades rurais com produção diária."""
            domain = [RuralProperty]
            range = [DailyProduction]

        class HasMonthlyProduction(ObjectProperty):
            """Relaciona propriedades rurais com produção mensal."""
            domain = [RuralProperty]
            range = [MonthlyProduction]

        class HasYearlyProduction(ObjectProperty):
            """Relaciona propriedades rurais com produção anual."""
            domain = [RuralProperty]
            range = [YearlyProduction]

        # class reproducers(DataProperty):
        #     """Número de reprodutores."""
        #     domain = [RuralProperty]
        #     range = [int]

        # class dryCows(DataProperty):
        #     """Número de vacas secas."""
        #     domain = [RuralProperty, DairyCattle]
        #     range = [int]

        # class pregnantHeifers(DataProperty):
        #     """Número de novilhas prenhas."""
        #     domain = [RuralProperty]
        #     range = [int]

        # class heifersInRaising(DataProperty):
        #     """Número de novilhas em criação."""
        #     domain = [RuralProperty]
        #     range = [int]

        # class sucklingCalvesFemale(DataProperty):
        #     """Número de bezerros fêmeas em amamentação."""
        #     domain = [RuralProperty]
        #     range = [int]

        # class sucklingCalvesMale(DataProperty):
        #     """Número de bezerros machos em amamentação."""
        #     domain = [RuralProperty]
        #     range = [int]

        # class maleCalvesInRaising(DataProperty):
        #     """Número de bezerros machos em criação."""
        #     domain = [RuralProperty]
        #     range = [int]

        # class maleCalvesInFattening(DataProperty):
        #     """Número de bezerros machos em engorda."""
        #     domain = [RuralProperty]
        #     range = [int]

        # class draftAndBreedingBulls(DataProperty):
        #     """Número de touros de tração e reprodução."""
        #     domain = [RuralProperty]
        #     range = [int]

        # class equinesAndMules(DataProperty):
        #     """Número de equinos e mulas."""
        #     domain = [RuralProperty]
        #     range = [int]


def create_rules(onto):
    """Creates SWRL rules for the ontology."""
    with onto:
        rule_milk_production_cattle = Imp()
        rule_milk_production_cattle.set_as_rule(
            'Cattle(?cattle) ^ milkProduction(?cattle, ?production) -> DairyCattle(?cattle)'
        )
        
        rule_enteric_factor_emissionTier1_individual = Imp()
        rule_enteric_factor_emissionTier1_individual.set_as_rule(
            'DairyCattle(?cattle) ^ '
            'emissionFactorDairyCattleTier1(?cattle, ?e) ^ '
            'daysOnFarm(?cattle, ?d) ^ '
            'multiply(?result, ?e, ?d) ^ '
            '-> individualEntericEmissionFactorTier1(?cattle, ?result)'
        )     

        rule_gross_energy_intake_per_individual = Imp()
        rule_gross_energy_intake_per_individual.set_as_rule(
            'DairyCattle(?cattle) ^ '
            'energyDensity(?cattle, ?e) ^ '
            'dryMatterIntake(?cattle, ?d) ^ '
            'multiply(?result, ?e, ?d) ^ '
            '-> grossEnergyIntake(?cattle, ?result)'
        ) 
        
        rule_enteric_factor_emissionTier2_individual = Imp()
        rule_enteric_factor_emissionTier2_individual.set_as_rule(
            'Cattle(?cattle) ^ '
            'grossEnergyIntake(?cattle, ?gei) ^ '
            'daysOnFarm(?cattle, ?d) ^ '
            'emissionFactorTier2(?cattle, ?ef) ^'
            'multiply(?result, ?gei, ?d, ?ef, 0.01) ^ '
            'divide(?finalResult, ?result, 55.65) ^ '
            '-> individualEntericEmissionFactorTier2(?cattle, ?finalResult)'
        )
        
        rule_enteric_emissionTier1_individual = Imp()
        rule_enteric_emissionTier1_individual.set_as_rule(
            'Cattle(?cattle) ^ '
            'individualEntericEmissionFactorTier1(?cattle, ?eeft1) ^ '
            'gwp(?cattle, ?gwp) ^ '
            'multiply(?result, ?eeft1, ?gwp, 0.001) ^ '
            '-> individualEntericEmissionTier1(?cattle, ?finalResult)'
        )  

        rule_enteric_emissionTier2_individual = Imp()
        rule_enteric_emissionTier2_individual.set_as_rule(
            'Cattle(?cattle) ^ '
            'individualEntericEmissionFactorTier2(?cattle, ?eeft2) ^ '
            'gwp(?cattle, ?gwp) ^ '
            'multiply(?result, ?eeft2, ?gwp, 0.001) ^ '
            '-> individualEntericEmissionTier2(?cattle, ?finalResult)'
        )

        # Additional rules
        rule_daily_milk_production = Imp()
        rule_daily_milk_production.set_as_rule(
            'DairyCattle(?cattle) ^ milkProduction(?cattle, ?dailyProduction) ^ '
            'timeGranularity(?cattle, "Daily") ^ '
            '-> dailyMilkProductionTotal(?cattle, ?dailyProduction)'
        )

        rule_monthly_milk_production = Imp()
        rule_monthly_milk_production.set_as_rule(
            'DairyCattle(?cattle) ^ milkProduction(?cattle, ?dailyProduction) ^ '
            'timeGranularity(?cattle, "Monthly") ^ '
            'multiply(?monthlyProduction, ?dailyProduction, 30) ^ '
            '-> monthlyMilkProductionTotal(?cattle, ?monthlyProduction)'
        )

        rule_yearly_milk_production = Imp()
        rule_yearly_milk_production.set_as_rule(
            'DairyCattle(?cattle) ^ milkProduction(?cattle, ?dailyProduction) ^ '
            'timeGranularity(?cattle, "Yearly") ^ '
            'multiply(?yearlyProduction, ?dailyProduction, 365) ^ '
            '-> yearlyMilkProductionTotal(?cattle, ?yearlyProduction)'
        )

        # rule_total_emissions_tier1 = Imp()
        # rule_total_emissions_tier1.set_as_rule(
        #     'RuralProperty(?property) ^ '
        #     'HasCattleGroup(?property, ?cattle) ^ '
        #     'individualEntericEmissionTier1(?cattle, ?emission) ^ '
        #     'swrlb:add(?totalEmission, ?totalEmission, ?emission) ^ '
        #     '-> totalEmissionsTier1(?property, ?totalEmission)'
        # )

        # rule_total_emissions_tier2 = Imp()
        # rule_total_emissions_tier2.set_as_rule(
        #     'RuralProperty(?property) ^ '
        #     'HasCattleGroup(?property, ?cattle) ^ '
        #     'individualEntericEmissionTier2(?cattle, ?emission) ^ '
        #     'swrlb:add(?totalEmission, ?totalEmission, ?emission) ^ '
        #     '-> totalEmissionsTier2(?property, ?totalEmission)'
        # )

        # rule_check_inconsistencies = Imp()
        # rule_check_inconsistencies.set_as_rule(
        #     'Cattle(?cattle) ^ milkProduction(?cattle, ?production) ^ '
        #     'swrlb:lessThan(?production, 0) ^ '
        #     '-> InconsistentData(?cattle)'
        # )

        # rule_check_future_dates = Imp()
        # rule_check_future_dates.set_as_rule(
        #     'MeasurementData(?data) ^ measurementDate(?data, ?date) ^ '
        #     'swrlb:greaterThan(?date, swrlb:now()) ^ '
        #     '-> InconsistentData(?data)'
        # )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        generate_ontology()
        logger.info("Ontology successfully generated.")
    except Exception as exc:
        logger.exception("Error generating ontology: %s", exc)
        raise
