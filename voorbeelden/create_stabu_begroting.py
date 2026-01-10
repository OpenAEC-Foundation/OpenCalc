#!/usr/bin/env python3
"""
Script om een voorbeeldbegroting te maken met STABU-codering
STABU hoofdstukindeling volgens NL-SfB/STABU standaard
"""

import sys
from pathlib import Path

# Voeg project root toe aan path
sys.path.insert(0, str(Path(__file__).parent.parent))

import ifcopenshell
import ifcopenshell.api
from datetime import datetime


def create_stabu_begroting():
    """Maak een begroting met STABU-codering"""

    # Nieuw IFC bestand
    ifc = ifcopenshell.file(schema="IFC4")

    # Project
    project = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
    ifcopenshell.api.run("attribute.edit_attributes", ifc, product=project, attributes={
        "Name": "Nieuwbouw Woning - STABU Begroting"
    })

    # Units
    ifcopenshell.api.run("unit.assign_unit", ifc, length={"is_metric": True, "raw": "METRE"})

    # Cost Schedule
    schedule = ifcopenshell.api.run("cost.add_cost_schedule", ifc,
        name="STABU Begroting Nieuwbouw Woning",
        predefined_type="BUDGET"
    )

    # STABU Hoofdstukken volgens standaard indeling
    # Gebaseerd op de STABU-systematiek (vereenvoudigd)

    stabu_chapters = [
        # (code, naam, items)
        ("00", "Algemeen", [
            ("00.01", "Bouwplaatsvoorzieningen", "st", 1, 2500.00),
            ("00.02", "Uitzetwerk", "st", 1, 1500.00),
            ("00.03", "Bouwbegeleiding", "st", 1, 3500.00),
        ]),
        ("10", "Stut- en sloopwerk", [
            ("10.10", "Slopen bestaande fundering", "m³", 15.0, 45.00),
            ("10.20", "Afvoeren sloopmateriaal", "m³", 20.0, 35.00),
        ]),
        ("16", "Bouwkundige keuringen", [
            ("16.10", "Constructieve keuring", "st", 1, 850.00),
            ("16.20", "Bouwtechnische opname", "st", 1, 650.00),
        ]),
        ("20", "Funderingswerk", [
            ("21.10", "Ontgraven bouwput", "m³", 85.0, 12.50),
            ("21.20", "Aanvullen zand", "m³", 25.0, 22.00),
            ("22.10", "Heipalen prefab beton", "st", 24, 285.00),
            ("22.20", "Heien incl. stellen", "st", 24, 125.00),
            ("23.10", "Funderingsbalken", "m", 42.0, 95.00),
            ("23.20", "Strookfundering gewapend beton C30/37", "m³", 18.5, 185.00),
            ("23.30", "Vloer op zand begane grond", "m²", 95.0, 65.00),
        ]),
        ("21", "Buitenwanden", [
            ("21.10", "Buitenspouwblad kalkzandsteen", "m²", 185.0, 72.00),
            ("21.20", "Spouwankers RVS", "st", 740, 1.25),
            ("21.30", "Spouwisolatie minerale wol 150mm", "m²", 185.0, 28.00),
            ("21.40", "Binnenspouwblad kalkzandsteen", "m²", 185.0, 58.00),
        ]),
        ("22", "Binnenwanden", [
            ("22.10", "Dragende binnenwanden kalkzandsteen", "m²", 65.0, 52.00),
            ("22.20", "Niet-dragende scheidingswanden", "m²", 85.0, 38.00),
            ("22.30", "Cellenbeton wandblokken", "m²", 45.0, 42.00),
        ]),
        ("23", "Vloeren", [
            ("23.10", "Verdiepingsvloer kanaalplaten", "m²", 95.0, 125.00),
            ("23.20", "Druklaag gewapend", "m²", 95.0, 18.00),
            ("23.30", "Vloerisolatie EPS", "m²", 95.0, 22.00),
        ]),
        ("24", "Trappen en hellingen", [
            ("24.10", "Bordestrap beton prefab", "st", 1, 2850.00),
            ("24.20", "Trapleuning hout", "m", 8.0, 145.00),
        ]),
        ("27", "Daken", [
            ("27.10", "Kapconstructie naaldhout", "m²", 110.0, 95.00),
            ("27.20", "Dakbeschot vuren", "m²", 110.0, 18.00),
            ("27.30", "Dampscherm PE-folie", "m²", 110.0, 4.50),
            ("27.40", "Dakisolatie PIR 140mm", "m²", 110.0, 48.00),
            ("27.50", "Onderdakfolie", "m²", 110.0, 6.00),
            ("27.60", "Tengels en panlatten", "m²", 110.0, 12.00),
            ("27.70", "Dakpannen keramisch", "m²", 110.0, 42.00),
        ]),
        ("28", "Hoofddraagconstructie", [
            ("28.10", "Lateien gewapend beton", "st", 12, 95.00),
            ("28.20", "Onderslagen staal", "st", 6, 185.00),
            ("28.30", "Betonnen dorpels", "m", 24.0, 45.00),
        ]),
        ("30", "Buitenkozijnen, -ramen en -deuren", [
            ("31.10", "Kozijnen kunststof wit", "st", 14, 450.00),
            ("31.20", "Voordeur met kozijn", "st", 1, 1850.00),
            ("31.30", "Achterdeur met kozijn", "st", 1, 1250.00),
            ("32.10", "HR++ beglazing", "m²", 32.0, 165.00),
            ("32.20", "Drievoudig glas", "m²", 8.0, 225.00),
        ]),
        ("32", "Binnenkozijnen en -deuren", [
            ("32.10", "Binnendeurkozijnen stomp", "st", 12, 185.00),
            ("32.20", "Binnendeuren opdek", "st", 12, 165.00),
            ("32.30", "Schuifdeuren", "st", 2, 485.00),
        ]),
        ("33", "Luiken en vensters", [
            ("33.10", "Dakramen HR++", "st", 4, 685.00),
        ]),
        ("40", "Stukadoorswerk", [
            ("41.10", "Wanden stucwerk binnen", "m²", 320.0, 24.00),
            ("41.20", "Plafonds stucwerk", "m²", 185.0, 28.00),
            ("41.30", "Buitengevelstuc", "m²", 45.0, 38.00),
        ]),
        ("42", "Tegelwerk", [
            ("42.10", "Wandtegels badkamer", "m²", 35.0, 65.00),
            ("42.20", "Wandtegels keuken", "m²", 8.0, 55.00),
            ("42.30", "Vloertegels keramisch", "m²", 45.0, 58.00),
        ]),
        ("43", "Dekvloeren en vloersystemen", [
            ("43.10", "Anhydrietvloer", "m²", 165.0, 24.00),
            ("43.20", "Vloerverwarming systeem", "m²", 95.0, 42.00),
        ]),
        ("45", "Plafonds", [
            ("45.10", "Systeemplafond badkamer", "m²", 12.0, 65.00),
            ("45.20", "Systeemplafond toilet", "m²", 4.0, 65.00),
        ]),
        ("48", "Schilderwerk", [
            ("48.10", "Binnenschilderwerk wanden", "m²", 320.0, 12.00),
            ("48.20", "Binnenschilderwerk houtwerk", "m²", 85.0, 28.00),
            ("48.30", "Buitenschilderwerk", "m²", 45.0, 32.00),
        ]),
        ("52", "Afvoeren en hemelwaterafvoer", [
            ("52.10", "Riolering binnenriolering", "m", 35.0, 45.00),
            ("52.20", "HWA dakgoten en afvoeren", "m", 28.0, 65.00),
            ("52.30", "Ontstoppingsstukken", "st", 6, 35.00),
        ]),
        ("53", "Waterleidinginstallatie", [
            ("53.10", "Waterleidingen koper", "m", 65.0, 28.00),
            ("53.20", "Watermeter aansluiting", "st", 1, 450.00),
        ]),
        ("54", "Gasinstallatie", [
            ("54.10", "Gasleidingen", "m", 25.0, 35.00),
            ("54.20", "Gasmeter aansluiting", "st", 1, 385.00),
        ]),
        ("55", "Koeling en verwarming", [
            ("55.10", "CV-ketel HR107", "st", 1, 2850.00),
            ("55.20", "Radiatoren", "st", 12, 285.00),
            ("55.30", "Vloerverwarmingsverdeler", "st", 2, 485.00),
            ("55.40", "Thermostaat slimme regeling", "st", 1, 285.00),
        ]),
        ("56", "Ventilatie en luchtbehandeling", [
            ("56.10", "Mechanische ventilatie unit", "st", 1, 1850.00),
            ("56.20", "Ventilatiekanalen", "m", 45.0, 28.00),
            ("56.30", "Roosters en afzuigventielen", "st", 12, 45.00),
        ]),
        ("60", "Elektrotechnische installaties", [
            ("61.10", "Meterkast compleet", "st", 1, 1250.00),
            ("61.20", "Elektraleidingen", "m", 450.0, 8.50),
            ("61.30", "Wandcontactdozen", "st", 45, 25.00),
            ("61.40", "Lichtpunten", "st", 28, 35.00),
            ("61.50", "Schakelmateriaal", "st", 32, 18.00),
            ("61.60", "Aarding en potentiaalvereffening", "st", 1, 385.00),
        ]),
        ("64", "Communicatie-installatie", [
            ("64.10", "Datapunten CAT6", "st", 12, 85.00),
            ("64.20", "Glasvezelaansluiting", "st", 1, 285.00),
        ]),
        ("70", "Sanitaire installaties", [
            ("71.10", "Closetcombinatie", "st", 2, 485.00),
            ("71.20", "Wastafel met onderkast", "st", 2, 385.00),
            ("71.30", "Douche compleet", "st", 1, 1250.00),
            ("71.40", "Ligbad", "st", 1, 850.00),
            ("71.50", "Keukenblok compleet", "st", 1, 4500.00),
            ("71.60", "Kranen sanitair", "st", 8, 145.00),
        ]),
        ("73", "Keukeninstallatie", [
            ("73.10", "Afzuigkap", "st", 1, 485.00),
            ("73.20", "Kookplaat inductie", "st", 1, 650.00),
            ("73.30", "Oven inbouw", "st", 1, 485.00),
        ]),
        ("90", "Terrein", [
            ("90.10", "Bestrating terras", "m²", 35.0, 65.00),
            ("90.20", "Oprit bestrating", "m²", 25.0, 55.00),
            ("90.30", "Tuinaanleg basis", "m²", 85.0, 28.00),
            ("90.40", "Erfafscheiding", "m", 45.0, 75.00),
        ]),
    ]

    # Maak hoofdstukken en items
    all_root_items = []

    for chapter_code, chapter_name, items in stabu_chapters:
        # Maak hoofdstuk
        chapter = ifcopenshell.api.run("cost.add_cost_item", ifc,
            cost_schedule=schedule
        )
        ifcopenshell.api.run("cost.edit_cost_item", ifc,
            cost_item=chapter,
            attributes={"Name": chapter_name, "Identification": chapter_code}
        )
        all_root_items.append(chapter)

        # Maak items in hoofdstuk
        for item_code, item_name, unit, quantity, unit_price in items:
            cost_item = ifcopenshell.api.run("cost.add_cost_item", ifc,
                cost_item=chapter
            )
            ifcopenshell.api.run("cost.edit_cost_item", ifc,
                cost_item=cost_item,
                attributes={"Name": item_name, "Identification": item_code}
            )

            # Quantity
            if unit == "m²":
                ifc_quantity = ifc.create_entity("IfcQuantityArea",
                    Name=unit,
                    AreaValue=quantity
                )
            elif unit == "m³":
                ifc_quantity = ifc.create_entity("IfcQuantityVolume",
                    Name=unit,
                    VolumeValue=quantity
                )
            elif unit == "m":
                ifc_quantity = ifc.create_entity("IfcQuantityLength",
                    Name=unit,
                    LengthValue=quantity
                )
            else:  # st of andere
                ifc_quantity = ifc.create_entity("IfcQuantityCount",
                    Name=unit,
                    CountValue=quantity
                )

            cost_item.CostQuantities = (ifc_quantity,)

            # Cost value
            cost_value = ifc.create_entity("IfcCostValue",
                AppliedValue=ifc.create_entity("IfcMonetaryMeasure", unit_price)
            )
            cost_item.CostValues = (cost_value,)

    # Assign items to schedule
    ifcopenshell.api.run("cost.assign_cost_item_quantity", ifc,
        cost_item=all_root_items[0],
        products=[]
    )

    # Assign all root items to schedule via IfcRelAssignsToControl
    ifc.create_entity("IfcRelAssignsToControl",
        GlobalId=ifcopenshell.guid.new(),
        RelatedObjects=all_root_items,
        RelatingControl=schedule
    )

    # Sla op
    output_path = Path(__file__).parent / "woning_stabu_begroting.ifc"
    ifc.write(str(output_path))
    print(f"STABU begroting opgeslagen: {output_path}")

    # Bereken totaal
    total = 0
    for chapter_code, chapter_name, items in stabu_chapters:
        chapter_total = sum(qty * price for _, _, _, qty, price in items)
        total += chapter_total
        print(f"  {chapter_code} {chapter_name}: € {chapter_total:,.2f}")

    print(f"\nDirecte kosten: € {total:,.2f}")
    print(f"AK (8%): € {total * 0.08:,.2f}")
    print(f"W&R (3%): € {total * 1.08 * 0.03:,.2f}")
    aanneemsom = total * 1.08 * 1.03
    print(f"Aanneemsom excl. BTW: € {aanneemsom:,.2f}")
    print(f"BTW (21%): € {aanneemsom * 0.21:,.2f}")
    print(f"TOTAAL incl. BTW: € {aanneemsom * 1.21:,.2f}")


if __name__ == "__main__":
    create_stabu_begroting()
