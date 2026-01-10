"""
STABU Begroting Generator
Genereert een IFC kostenbegroting op basis van STABU-codering voor een woning
"""

import ifcopenshell
import ifcopenshell.api
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class STABUPost:
    """Een STABU begrotingspost"""
    code: str
    omschrijving: str
    hoeveelheid: float
    eenheid: str
    eenheidsprijs: float

    @property
    def totaal(self) -> float:
        return self.hoeveelheid * self.eenheidsprijs


# STABU Codering structuur voor woningbouw
STABU_HOOFDSTUKKEN = {
    "00": "Algemeen",
    "21": "Buitenwanden",
    "22": "Binnenwanden",
    "23": "Vloeren",
    "24": "Trappen en hellingen",
    "27": "Daken",
    "28": "Hoofddraagconstructie",
    "31": "Buitenkozijnen, -ramen en -deuren",
    "32": "Binnenkozijnen en -deuren",
    "33": "Luiken en vensters",
    "34": "Balustrades en leuningen",
    "41": "Binnenwandafwerkingen",
    "42": "Vloerafwerkingen",
    "43": "Plafondafwerkingen",
    "45": "Afwerkingen buitenwanden",
    "52": "Riolering en HWA",
    "53": "Waterleidingen",
    "54": "Gasleidingen",
    "61": "Elektrische installaties",
    "64": "Verwarmingsinstallaties",
    "65": "Ventilatie en luchtbehandeling",
    "73": "Keukeninstallaties",
    "74": "Sanitair",
    "90": "Terrein",
}


def genereer_woning_begroting() -> Dict[str, List[STABUPost]]:
    """
    Genereer een realistische begroting voor een eengezinswoning.

    Returns:
        Dictionary met STABU hoofdstukken en bijbehorende posten
    """
    begroting = {}

    # 00 - Algemeen
    begroting["00"] = [
        STABUPost("00.01.10", "Bouwplaatsinrichting", 1, "ps", 3500.00),
        STABUPost("00.02.10", "Uitzetten en maatvoering", 1, "ps", 1200.00),
        STABUPost("00.03.10", "Bouwplaatsbeveiliging", 1, "ps", 850.00),
        STABUPost("00.05.10", "Bouwstroom en -water", 1, "ps", 750.00),
    ]

    # 21 - Buitenwanden
    begroting["21"] = [
        STABUPost("21.11.10", "Metselwerk buitenspouwblad gevelsteen", 145, "m2", 85.00),
        STABUPost("21.11.20", "Metselwerk binnenspouwblad kalkzandsteen", 145, "m2", 52.00),
        STABUPost("21.12.10", "Spouwisolatie minerale wol 100mm", 145, "m2", 28.00),
        STABUPost("21.21.10", "Lateien prefab beton", 12, "st", 145.00),
        STABUPost("21.22.10", "Raveelconstructies", 4, "st", 320.00),
    ]

    # 22 - Binnenwanden
    begroting["22"] = [
        STABUPost("22.11.10", "Binnenwand kalkzandsteen 100mm", 85, "m2", 48.00),
        STABUPost("22.11.20", "Binnenwand metalstud 100mm", 42, "m2", 62.00),
        STABUPost("22.12.10", "Scheidingswand gipsblokken 70mm", 28, "m2", 38.00),
    ]

    # 23 - Vloeren
    begroting["23"] = [
        STABUPost("23.11.10", "Begane grondvloer gewapend beton", 75, "m2", 95.00),
        STABUPost("23.11.20", "Vloerisolatie EPS 120mm", 75, "m2", 32.00),
        STABUPost("23.21.10", "Verdiepingsvloer kanaalplaat 200mm", 68, "m2", 78.00),
        STABUPost("23.21.20", "Druklaag verdiepingsvloer", 68, "m2", 18.00),
    ]

    # 24 - Trappen
    begroting["24"] = [
        STABUPost("24.11.10", "Trap beton prefab", 1, "st", 2850.00),
        STABUPost("24.12.10", "Trapafwerking hardhout", 1, "st", 1650.00),
    ]

    # 27 - Daken
    begroting["27"] = [
        STABUPost("27.11.10", "Dakconstructie kap gezaagd hout", 95, "m2", 68.00),
        STABUPost("27.12.10", "Dakisolatie PIR 140mm", 95, "m2", 45.00),
        STABUPost("27.21.10", "Dakbedekking keramische pannen", 95, "m2", 42.00),
        STABUPost("27.22.10", "Nokvorst en hulpstukken", 12, "m1", 38.00),
        STABUPost("27.31.10", "Dakgoten zink 150mm", 22, "m1", 65.00),
        STABUPost("27.31.20", "Hemelwaterafvoer zink 80mm", 8, "m1", 48.00),
    ]

    # 28 - Hoofddraagconstructie
    begroting["28"] = [
        STABUPost("28.11.10", "Funderingsstroken ongewapend beton", 42, "m1", 125.00),
        STABUPost("28.12.10", "Funderingsbalken prefab beton", 28, "m1", 185.00),
        STABUPost("28.21.10", "Staalconstructie overspanning", 2, "st", 1850.00),
    ]

    # 31 - Buitenkozijnen
    begroting["31"] = [
        STABUPost("31.11.10", "Kozijnen kunststof wit", 12, "st", 485.00),
        STABUPost("31.12.10", "Openslaande deuren kunststof", 2, "st", 1250.00),
        STABUPost("31.21.10", "Beglazing HR++ 4-16-4", 28, "m2", 125.00),
        STABUPost("31.31.10", "Voordeurkozijn hardhout incl. deur", 1, "st", 2150.00),
        STABUPost("31.32.10", "Achterdeurkozijn hardhout incl. deur", 1, "st", 1650.00),
    ]

    # 32 - Binnenkozijnen
    begroting["32"] = [
        STABUPost("32.11.10", "Binnendeuren opdek stompe uitvoering", 8, "st", 285.00),
        STABUPost("32.12.10", "Binnendeuren paneeldeur", 4, "st", 425.00),
        STABUPost("32.21.10", "Binnenkozijnen MDF", 12, "st", 145.00),
    ]

    # 34 - Balustrades
    begroting["34"] = [
        STABUPost("34.11.10", "Balustrade trap hout", 4, "m1", 185.00),
        STABUPost("34.12.10", "Balustrade vide staal", 2, "m1", 425.00),
    ]

    # 41 - Binnenwandafwerkingen
    begroting["41"] = [
        STABUPost("41.11.10", "Stucwerk wanden gipspleister", 285, "m2", 18.00),
        STABUPost("41.12.10", "Tegelwerk badkamer wandtegels", 32, "m2", 75.00),
        STABUPost("41.12.20", "Tegelwerk toilet wandtegels", 12, "m2", 68.00),
        STABUPost("41.21.10", "Schilderwerk wanden latex", 285, "m2", 8.50),
    ]

    # 42 - Vloerafwerkingen
    begroting["42"] = [
        STABUPost("42.11.10", "Dekvloer cementgebonden 60mm", 140, "m2", 28.00),
        STABUPost("42.12.10", "Vloertegels keramisch 60x60", 45, "m2", 85.00),
        STABUPost("42.13.10", "Laminaatvloer incl. ondervloer", 75, "m2", 42.00),
        STABUPost("42.14.10", "Vloertegels badkamer antislip", 8, "m2", 95.00),
    ]

    # 43 - Plafondafwerkingen
    begroting["43"] = [
        STABUPost("43.11.10", "Stucwerk plafonds gipspleister", 140, "m2", 22.00),
        STABUPost("43.21.10", "Schilderwerk plafonds latex", 140, "m2", 7.50),
    ]

    # 45 - Buitenwandafwerkingen
    begroting["45"] = [
        STABUPost("45.11.10", "Voegwerk gevelmetselwerk", 145, "m2", 12.00),
        STABUPost("45.21.10", "Buitenkozijnen afwerking", 12, "st", 48.00),
    ]

    # 52 - Riolering
    begroting["52"] = [
        STABUPost("52.11.10", "Binnenriolering PVC 110mm", 35, "m1", 42.00),
        STABUPost("52.12.10", "Ontstoppingsstukken", 6, "st", 28.00),
        STABUPost("52.21.10", "Buitenriolering tot perceelgrens", 12, "m1", 68.00),
    ]

    # 53 - Waterleidingen
    begroting["53"] = [
        STABUPost("53.11.10", "Waterleidingen koud MPE", 45, "m1", 18.00),
        STABUPost("53.12.10", "Waterleidingen warm MPE geisoleerd", 32, "m1", 24.00),
        STABUPost("53.21.10", "Watermeter en aansluitset", 1, "st", 285.00),
    ]

    # 54 - Gasleidingen
    begroting["54"] = [
        STABUPost("54.11.10", "Gasleiding staal", 8, "m1", 45.00),
        STABUPost("54.21.10", "Gasmeter en aansluitset", 1, "st", 185.00),
    ]

    # 61 - Elektrische installaties
    begroting["61"] = [
        STABUPost("61.11.10", "Groepenkast 12-groeps", 1, "st", 850.00),
        STABUPost("61.12.10", "Bekabeling installatiedraad", 450, "m1", 4.50),
        STABUPost("61.21.10", "Wandcontactdozen enkel", 32, "st", 18.00),
        STABUPost("61.21.20", "Wandcontactdozen dubbel", 12, "st", 28.00),
        STABUPost("61.22.10", "Schakelaars enkel", 14, "st", 15.00),
        STABUPost("61.22.20", "Schakelaars wissel", 6, "st", 22.00),
        STABUPost("61.31.10", "Lichtpunten plafond", 18, "st", 35.00),
        STABUPost("61.32.10", "Lichtpunten wand", 8, "st", 28.00),
        STABUPost("61.41.10", "Buitenverlichting gevelmontage", 3, "st", 85.00),
    ]

    # 64 - Verwarming
    begroting["64"] = [
        STABUPost("64.11.10", "CV-ketel HR-107 combi 28kW", 1, "st", 1850.00),
        STABUPost("64.12.10", "CV-leidingen koper", 85, "m1", 18.00),
        STABUPost("64.21.10", "Radiatoren type 22 versch. maten", 10, "st", 285.00),
        STABUPost("64.22.10", "Radiatorkranen thermostatisch", 10, "st", 42.00),
        STABUPost("64.31.10", "Vloerverwarming begane grond", 45, "m2", 58.00),
    ]

    # 65 - Ventilatie
    begroting["65"] = [
        STABUPost("65.11.10", "Mechanische ventilatie unit C+", 1, "st", 1450.00),
        STABUPost("65.12.10", "Luchtkanalen spirobuis", 35, "m1", 28.00),
        STABUPost("65.21.10", "Ventilatieroosters afvoer", 6, "st", 48.00),
        STABUPost("65.22.10", "Ventilatieroosters toevoer", 8, "st", 38.00),
    ]

    # 73 - Keuken
    begroting["73"] = [
        STABUPost("73.11.10", "Keukenblok compleet 4.5m1", 1, "st", 8500.00),
        STABUPost("73.12.10", "Keukenapparatuur basis pakket", 1, "st", 2850.00),
        STABUPost("73.21.10", "Aanrechtblad composiet", 4.5, "m1", 385.00),
    ]

    # 74 - Sanitair
    begroting["74"] = [
        STABUPost("74.11.10", "Toiletcombinatie hangend incl. reservoir", 2, "st", 485.00),
        STABUPost("74.12.10", "Wastafel opbouw incl. kraan", 2, "st", 385.00),
        STABUPost("74.13.10", "Badkuip 170x75 acryl", 1, "st", 650.00),
        STABUPost("74.14.10", "Douchecabine 90x90", 1, "st", 850.00),
        STABUPost("74.21.10", "Badkamerkranen set", 1, "st", 485.00),
        STABUPost("74.22.10", "Douche thermostaatkraan", 1, "st", 285.00),
        STABUPost("74.31.10", "Badkameraccessoires set", 2, "st", 125.00),
    ]

    # 90 - Terrein
    begroting["90"] = [
        STABUPost("90.11.10", "Bestrating oprit klinkers", 25, "m2", 65.00),
        STABUPost("90.12.10", "Bestrating terras tegels", 18, "m2", 58.00),
        STABUPost("90.21.10", "Erfafscheiding schutting 180cm", 24, "m1", 85.00),
        STABUPost("90.31.10", "Beplanting basis", 1, "ps", 1250.00),
    ]

    return begroting


def maak_ifc_begroting(output_path: str) -> str:
    """
    Maak een IFC bestand met de complete STABU begroting.

    Args:
        output_path: Pad waar het IFC bestand opgeslagen wordt

    Returns:
        Pad naar het aangemaakte bestand
    """
    # Maak nieuw IFC bestand
    ifc = ifcopenshell.file(schema="IFC4")

    # Project aanmaken
    project = ifcopenshell.api.run(
        "root.create_entity",
        ifc,
        ifc_class="IfcProject",
        name="Eengezinswoning Begroting STABU"
    )

    # Eenheden instellen
    ifcopenshell.api.run(
        "unit.assign_unit",
        ifc,
        length={"is_metric": True, "raw": "METRE"},
        area={"is_metric": True, "raw": "SQUARE_METRE"},
        volume={"is_metric": True, "raw": "CUBIC_METRE"}
    )

    # Kostenschema aanmaken
    schedule = ifcopenshell.api.run(
        "cost.add_cost_schedule",
        ifc,
        name="Begroting Eengezinswoning",
        predefined_type="BUDGET"
    )
    schedule.Status = "CONCEPT"
    schedule.SubmittedOn = datetime.now().strftime("%Y-%m-%d")

    # Genereer begroting data
    begroting = genereer_woning_begroting()

    totaal_begroting = 0.0

    # Voeg hoofdstukken en posten toe
    for code, naam in STABU_HOOFDSTUKKEN.items():
        if code not in begroting:
            continue

        posten = begroting[code]
        if not posten:
            continue

        # Maak hoofdstuk
        hoofdstuk = ifcopenshell.api.run(
            "cost.add_cost_item",
            ifc,
            cost_schedule=schedule
        )
        hoofdstuk.Name = naam
        hoofdstuk.Identification = code

        hoofdstuk_totaal = 0.0

        # Voeg posten toe aan hoofdstuk
        for post in posten:
            cost_item = ifcopenshell.api.run(
                "cost.add_cost_item",
                ifc,
                cost_item=hoofdstuk
            )
            cost_item.Name = post.omschrijving
            cost_item.Identification = post.code

            # Hoeveelheid toevoegen
            if post.eenheid == "m2":
                qty_class = "IfcQuantityArea"
                qty_attr = "AreaValue"
            elif post.eenheid == "m1":
                qty_class = "IfcQuantityLength"
                qty_attr = "LengthValue"
            elif post.eenheid == "m3":
                qty_class = "IfcQuantityVolume"
                qty_attr = "VolumeValue"
            else:  # st, ps, etc.
                qty_class = "IfcQuantityCount"
                qty_attr = "CountValue"

            quantity = ifcopenshell.api.run(
                "cost.add_cost_item_quantity",
                ifc,
                cost_item=cost_item,
                ifc_class=qty_class
            )
            quantity.Name = post.eenheid
            setattr(quantity, qty_attr, post.hoeveelheid)

            # Eenheidsprijs toevoegen
            cost_value = ifcopenshell.api.run(
                "cost.add_cost_value",
                ifc,
                parent=cost_item
            )
            cost_value.AppliedValue = ifc.createIfcMonetaryMeasure(post.eenheidsprijs)
            cost_value.Category = "Eenheidsprijs"

            hoofdstuk_totaal += post.totaal

        totaal_begroting += hoofdstuk_totaal

    # Opslaan
    output = Path(output_path)
    ifc.write(str(output))

    print(f"\n{'='*60}")
    print(f"STABU Begroting gegenereerd")
    print(f"{'='*60}")
    print(f"Bestand: {output}")
    print(f"Totaal begroting: EUR {totaal_begroting:,.2f}")
    print(f"{'='*60}\n")

    return str(output)


def print_begroting_overzicht():
    """Print een overzicht van de gegenereerde begroting"""
    begroting = genereer_woning_begroting()

    print("\n" + "="*80)
    print("STABU BEGROTING - EENGEZINSWONING")
    print("="*80)

    totaal = 0.0

    for code in sorted(begroting.keys()):
        posten = begroting[code]
        naam = STABU_HOOFDSTUKKEN.get(code, "Onbekend")

        print(f"\n{code} - {naam}")
        print("-"*60)

        hoofdstuk_totaal = 0.0
        for post in posten:
            print(f"  {post.code}  {post.omschrijving[:40]:<40} "
                  f"{post.hoeveelheid:>8.2f} {post.eenheid:<4} "
                  f"x EUR {post.eenheidsprijs:>8.2f} = EUR {post.totaal:>10,.2f}")
            hoofdstuk_totaal += post.totaal

        print(f"  {'Subtotaal:':<52} EUR {hoofdstuk_totaal:>22,.2f}")
        totaal += hoofdstuk_totaal

    print("\n" + "="*80)
    print(f"TOTAAL BEGROTING: EUR {totaal:>52,.2f}")
    print("="*80 + "\n")

    return totaal


if __name__ == "__main__":
    # Print overzicht
    print_begroting_overzicht()

    # Genereer IFC
    output_path = Path(__file__).parent.parent / "data" / "woning_begroting_stabu.ifc"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    maak_ifc_begroting(str(output_path))
