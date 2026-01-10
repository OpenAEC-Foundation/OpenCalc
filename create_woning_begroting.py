#!/usr/bin/env python3
"""
Script om een standaard woningbegroting aan te maken in IFC formaat
"""

import ifcopenshell
import ifcopenshell.api
from pathlib import Path


def create_woning_begroting():
    """Maak een complete woningbegroting aan"""

    # Nieuw IFC bestand
    ifc = ifcopenshell.file(schema="IFC4")

    # Project aanmaken
    project = ifcopenshell.api.run(
        "root.create_entity", ifc,
        ifc_class="IfcProject",
        name="Woningbouw Project"
    )

    # Eenheden instellen
    ifcopenshell.api.run(
        "unit.assign_unit", ifc,
        length={"is_metric": True, "raw": "METRE"},
        area={"is_metric": True, "raw": "SQUARE_METRE"},
        volume={"is_metric": True, "raw": "CUBIC_METRE"}
    )

    # Cost Schedule aanmaken
    schedule = ifcopenshell.api.run(
        "cost.add_cost_schedule", ifc,
        name="Begroting Nieuwbouw Woning",
        predefined_type="BUDGET"
    )

    # Begrotingsstructuur definiëren
    begroting_data = [
        {
            "code": "01",
            "naam": "Grondwerk",
            "items": [
                {"code": "01.01", "naam": "Ontgraven bouwput", "eenheid": "m³", "hoeveelheid": 85.0, "prijs": 12.50},
                {"code": "01.02", "naam": "Afvoeren grond", "eenheid": "m³", "hoeveelheid": 65.0, "prijs": 18.00},
                {"code": "01.03", "naam": "Aanvullen zand", "eenheid": "m³", "hoeveelheid": 25.0, "prijs": 22.00},
            ]
        },
        {
            "code": "02",
            "naam": "Fundering",
            "items": [
                {"code": "02.01", "naam": "Strookfundering gewapend beton", "eenheid": "m³", "hoeveelheid": 18.5, "prijs": 185.00},
                {"code": "02.02", "naam": "Funderingsbalken", "eenheid": "m", "hoeveelheid": 42.0, "prijs": 95.00},
                {"code": "02.03", "naam": "Vloer op zand begane grond", "eenheid": "m²", "hoeveelheid": 95.0, "prijs": 65.00},
            ]
        },
        {
            "code": "03",
            "naam": "Ruwbouw - Metselwerk",
            "items": [
                {"code": "03.01", "naam": "Buitenspouwblad kalkzandsteen", "eenheid": "m²", "hoeveelheid": 185.0, "prijs": 72.00},
                {"code": "03.02", "naam": "Binnenspouwblad kalkzandsteen", "eenheid": "m²", "hoeveelheid": 185.0, "prijs": 58.00},
                {"code": "03.03", "naam": "Spouwankers en isolatie", "eenheid": "m²", "hoeveelheid": 185.0, "prijs": 45.00},
                {"code": "03.04", "naam": "Binnenmuren draagconstructie", "eenheid": "m²", "hoeveelheid": 65.0, "prijs": 52.00},
                {"code": "03.05", "naam": "Scheidingswanden niet-dragend", "eenheid": "m²", "hoeveelheid": 85.0, "prijs": 38.00},
            ]
        },
        {
            "code": "04",
            "naam": "Ruwbouw - Beton",
            "items": [
                {"code": "04.01", "naam": "Verdiepingsvloer kanaalplaten", "eenheid": "m²", "hoeveelheid": 95.0, "prijs": 125.00},
                {"code": "04.02", "naam": "Lateien en onderslagen", "eenheid": "st", "hoeveelheid": 18.0, "prijs": 85.00},
                {"code": "04.03", "naam": "Betonnen dorpels", "eenheid": "m", "hoeveelheid": 24.0, "prijs": 45.00},
            ]
        },
        {
            "code": "05",
            "naam": "Dakconstructie",
            "items": [
                {"code": "05.01", "naam": "Kapconstructie hout", "eenheid": "m²", "hoeveelheid": 110.0, "prijs": 95.00},
                {"code": "05.02", "naam": "Dakbeschot en folie", "eenheid": "m²", "hoeveelheid": 110.0, "prijs": 28.00},
                {"code": "05.03", "naam": "Dakpannen keramisch", "eenheid": "m²", "hoeveelheid": 110.0, "prijs": 48.00},
                {"code": "05.04", "naam": "Dakisolatie PIR", "eenheid": "m²", "hoeveelheid": 110.0, "prijs": 55.00},
                {"code": "05.05", "naam": "Dakgoten en HWA", "eenheid": "m", "hoeveelheid": 28.0, "prijs": 65.00},
            ]
        },
        {
            "code": "06",
            "naam": "Kozijnen en Beglazing",
            "items": [
                {"code": "06.01", "naam": "Kozijnen kunststof wit", "eenheid": "st", "hoeveelheid": 14.0, "prijs": 450.00},
                {"code": "06.02", "naam": "Voordeur met kozijn", "eenheid": "st", "hoeveelheid": 1.0, "prijs": 1850.00},
                {"code": "06.03", "naam": "Achterdeur met kozijn", "eenheid": "st", "hoeveelheid": 1.0, "prijs": 1250.00},
                {"code": "06.04", "naam": "HR++ beglazing", "eenheid": "m²", "hoeveelheid": 32.0, "prijs": 165.00},
                {"code": "06.05", "naam": "Binnendeurenkozijnen", "eenheid": "st", "hoeveelheid": 12.0, "prijs": 185.00},
                {"code": "06.06", "naam": "Binnendeuren opdek", "eenheid": "st", "hoeveelheid": 12.0, "prijs": 145.00},
            ]
        },
        {
            "code": "07",
            "naam": "Afbouw - Stukadoorswerk",
            "items": [
                {"code": "07.01", "naam": "Stucwerk wanden", "eenheid": "m²", "hoeveelheid": 320.0, "prijs": 18.50},
                {"code": "07.02", "naam": "Stucwerk plafonds", "eenheid": "m²", "hoeveelheid": 95.0, "prijs": 22.00},
                {"code": "07.03", "naam": "Sierpleister buitengevel", "eenheid": "m²", "hoeveelheid": 45.0, "prijs": 35.00},
            ]
        },
        {
            "code": "08",
            "naam": "Afbouw - Tegelwerk",
            "items": [
                {"code": "08.01", "naam": "Wandtegels badkamer", "eenheid": "m²", "hoeveelheid": 28.0, "prijs": 85.00},
                {"code": "08.02", "naam": "Vloertegels badkamer", "eenheid": "m²", "hoeveelheid": 8.0, "prijs": 75.00},
                {"code": "08.03", "naam": "Wandtegels toilet", "eenheid": "m²", "hoeveelheid": 12.0, "prijs": 75.00},
                {"code": "08.04", "naam": "Vloertegels toilet", "eenheid": "m²", "hoeveelheid": 2.5, "prijs": 65.00},
                {"code": "08.05", "naam": "Tegelwerk keuken spatwand", "eenheid": "m²", "hoeveelheid": 4.5, "prijs": 95.00},
            ]
        },
        {
            "code": "09",
            "naam": "Schilderwerk",
            "items": [
                {"code": "09.01", "naam": "Binnenschilderwerk wanden", "eenheid": "m²", "hoeveelheid": 320.0, "prijs": 12.00},
                {"code": "09.02", "naam": "Binnenschilderwerk plafonds", "eenheid": "m²", "hoeveelheid": 95.0, "prijs": 14.00},
                {"code": "09.03", "naam": "Schilderwerk kozijnen binnen", "eenheid": "st", "hoeveelheid": 26.0, "prijs": 65.00},
                {"code": "09.04", "naam": "Schilderwerk buitenkozijnen", "eenheid": "st", "hoeveelheid": 14.0, "prijs": 85.00},
            ]
        },
        {
            "code": "10",
            "naam": "Vloerafwerking",
            "items": [
                {"code": "10.01", "naam": "Cementdekvloer", "eenheid": "m²", "hoeveelheid": 175.0, "prijs": 28.00},
                {"code": "10.02", "naam": "Vloerisolatie EPS", "eenheid": "m²", "hoeveelheid": 95.0, "prijs": 18.00},
                {"code": "10.03", "naam": "Laminaatvloer woonkamer", "eenheid": "m²", "hoeveelheid": 45.0, "prijs": 42.00},
                {"code": "10.04", "naam": "Laminaatvloer slaapkamers", "eenheid": "m²", "hoeveelheid": 48.0, "prijs": 38.00},
            ]
        },
        {
            "code": "11",
            "naam": "Elektra Installatie",
            "items": [
                {"code": "11.01", "naam": "Groepenkast 12 groepen", "eenheid": "st", "hoeveelheid": 1.0, "prijs": 850.00},
                {"code": "11.02", "naam": "Wandcontactdozen", "eenheid": "st", "hoeveelheid": 45.0, "prijs": 65.00},
                {"code": "11.03", "naam": "Lichtpunten plafond", "eenheid": "st", "hoeveelheid": 18.0, "prijs": 85.00},
                {"code": "11.04", "naam": "Schakelaars", "eenheid": "st", "hoeveelheid": 22.0, "prijs": 45.00},
                {"code": "11.05", "naam": "Bekabeling en buizen", "eenheid": "m", "hoeveelheid": 320.0, "prijs": 8.50},
            ]
        },
        {
            "code": "12",
            "naam": "Sanitair Installatie",
            "items": [
                {"code": "12.01", "naam": "Waterleiding aanleg", "eenheid": "m", "hoeveelheid": 65.0, "prijs": 42.00},
                {"code": "12.02", "naam": "Riolering binnenriolering", "eenheid": "m", "hoeveelheid": 45.0, "prijs": 55.00},
                {"code": "12.03", "naam": "Badkuip met mengkraan", "eenheid": "st", "hoeveelheid": 1.0, "prijs": 1250.00},
                {"code": "12.04", "naam": "Douchecabine compleet", "eenheid": "st", "hoeveelheid": 1.0, "prijs": 1450.00},
                {"code": "12.05", "naam": "Wastafel met mengkraan", "eenheid": "st", "hoeveelheid": 2.0, "prijs": 485.00},
                {"code": "12.06", "naam": "Toilet hangend met reservoir", "eenheid": "st", "hoeveelheid": 2.0, "prijs": 650.00},
                {"code": "12.07", "naam": "Keukenblok compleet", "eenheid": "st", "hoeveelheid": 1.0, "prijs": 4500.00},
            ]
        },
        {
            "code": "13",
            "naam": "Verwarming Installatie",
            "items": [
                {"code": "13.01", "naam": "CV-ketel HR107", "eenheid": "st", "hoeveelheid": 1.0, "prijs": 2850.00},
                {"code": "13.02", "naam": "Radiatoren paneel", "eenheid": "st", "hoeveelheid": 12.0, "prijs": 285.00},
                {"code": "13.03", "naam": "Vloerverwarming begane grond", "eenheid": "m²", "hoeveelheid": 65.0, "prijs": 55.00},
                {"code": "13.04", "naam": "CV-leidingwerk", "eenheid": "m", "hoeveelheid": 85.0, "prijs": 28.00},
                {"code": "13.05", "naam": "Thermostaat en regeling", "eenheid": "st", "hoeveelheid": 1.0, "prijs": 450.00},
            ]
        },
        {
            "code": "14",
            "naam": "Ventilatie",
            "items": [
                {"code": "14.01", "naam": "Mechanische ventilatie unit", "eenheid": "st", "hoeveelheid": 1.0, "prijs": 1850.00},
                {"code": "14.02", "naam": "Ventilatiekanalen", "eenheid": "m", "hoeveelheid": 45.0, "prijs": 35.00},
                {"code": "14.03", "naam": "Ventielen en roosters", "eenheid": "st", "hoeveelheid": 14.0, "prijs": 65.00},
            ]
        },
        {
            "code": "15",
            "naam": "Buitenwerk",
            "items": [
                {"code": "15.01", "naam": "Bestrating oprit", "eenheid": "m²", "hoeveelheid": 35.0, "prijs": 55.00},
                {"code": "15.02", "naam": "Terras tegels", "eenheid": "m²", "hoeveelheid": 25.0, "prijs": 48.00},
                {"code": "15.03", "naam": "Erfafscheiding/schutting", "eenheid": "m", "hoeveelheid": 28.0, "prijs": 125.00},
                {"code": "15.04", "naam": "Tuinaanleg basis", "eenheid": "m²", "hoeveelheid": 120.0, "prijs": 18.00},
            ]
        },
    ]

    # Hoofdstukken en items aanmaken
    for hoofdstuk_data in begroting_data:
        # Hoofdstuk aanmaken
        hoofdstuk = ifcopenshell.api.run(
            "cost.add_cost_item", ifc,
            cost_schedule=schedule
        )
        hoofdstuk.Name = hoofdstuk_data["naam"]
        hoofdstuk.Identification = hoofdstuk_data["code"]

        # Items aanmaken
        for item_data in hoofdstuk_data["items"]:
            item = ifcopenshell.api.run(
                "cost.add_cost_item", ifc,
                cost_item=hoofdstuk
            )
            item.Name = item_data["naam"]
            item.Identification = item_data["code"]

            # Hoeveelheid toevoegen
            eenheid = item_data["eenheid"]
            if eenheid == "m²":
                qty_class = "IfcQuantityArea"
                qty_attr = "AreaValue"
            elif eenheid == "m³":
                qty_class = "IfcQuantityVolume"
                qty_attr = "VolumeValue"
            elif eenheid == "m":
                qty_class = "IfcQuantityLength"
                qty_attr = "LengthValue"
            else:  # st (stuks)
                qty_class = "IfcQuantityCount"
                qty_attr = "CountValue"

            quantity = ifcopenshell.api.run(
                "cost.add_cost_item_quantity", ifc,
                cost_item=item,
                ifc_class=qty_class
            )
            quantity.Name = eenheid
            setattr(quantity, qty_attr, item_data["hoeveelheid"])

            # Prijs toevoegen
            value = ifcopenshell.api.run(
                "cost.add_cost_value", ifc,
                parent=item
            )
            ifcopenshell.api.run(
                "cost.edit_cost_value", ifc,
                cost_value=value,
                attributes={"AppliedValue": float(item_data["prijs"])}
            )

    # Opslaan
    output_path = Path(__file__).parent / "voorbeelden" / "woning_begroting.ifc"
    output_path.parent.mkdir(exist_ok=True)
    ifc.write(str(output_path))

    print(f"Begroting aangemaakt: {output_path}")
    return output_path


if __name__ == "__main__":
    create_woning_begroting()
