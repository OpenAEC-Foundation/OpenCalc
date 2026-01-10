"""
CostValue Model - Representeert een kostenwaarde (eenheidsprijs)
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class QuantityType(Enum):
    """Types hoeveelheden voor kostenposten"""
    COUNT = "IfcQuantityCount"       # Stuks
    LENGTH = "IfcQuantityLength"     # Meters
    AREA = "IfcQuantityArea"         # Vierkante meters
    VOLUME = "IfcQuantityVolume"     # Kubieke meters
    WEIGHT = "IfcQuantityWeight"     # Kilogram
    TIME = "IfcQuantityTime"         # Tijd
    NUMBER = "IfcQuantityNumber"     # Generiek nummer

    @property
    def unit_symbol(self) -> str:
        """Geeft het eenheidssymbool terug"""
        symbols = {
            "IfcQuantityCount": "st",
            "IfcQuantityLength": "m",
            "IfcQuantityArea": "m²",
            "IfcQuantityVolume": "m³",
            "IfcQuantityWeight": "kg",
            "IfcQuantityTime": "uur",
            "IfcQuantityNumber": "",
        }
        return symbols.get(self.value, "")

    @property
    def unit_name(self) -> str:
        """Geeft de volledige eenheidsnaam terug"""
        names = {
            "IfcQuantityCount": "stuks",
            "IfcQuantityLength": "meter",
            "IfcQuantityArea": "vierkante meter",
            "IfcQuantityVolume": "kubieke meter",
            "IfcQuantityWeight": "kilogram",
            "IfcQuantityTime": "uur",
            "IfcQuantityNumber": "nummer",
        }
        return names.get(self.value, "")


@dataclass
class CostValue:
    """
    Representeert een kostenwaarde (eenheidsprijs en hoeveelheid).

    Attributes:
        unit_price: Eenheidsprijs in euro's
        quantity: Hoeveelheid
        quantity_type: Type hoeveelheid (m², m³, stuks, etc.)
        category: Categorie van de kosten
        description: Omschrijving van de waarde
        ifc_cost_value: Referentie naar IFC object
        ifc_quantity: Referentie naar IFC quantity object
    """
    unit_price: float = 0.0
    quantity: float = 0.0
    quantity_type: QuantityType = QuantityType.COUNT
    category: str = ""
    description: str = ""
    ifc_cost_value: Optional[object] = field(default=None, repr=False)
    ifc_quantity: Optional[object] = field(default=None, repr=False)

    @property
    def total(self) -> float:
        """Bereken het totaal (quantity * unit_price)"""
        return self.quantity * self.unit_price

    @property
    def unit_symbol(self) -> str:
        """Geeft het eenheidssymbool terug"""
        return self.quantity_type.unit_symbol

    @property
    def unit_name(self) -> str:
        """Geeft de volledige eenheidsnaam terug"""
        return self.quantity_type.unit_name

    def format_price(self, currency: str = "€") -> str:
        """Formatteer de eenheidsprijs als tekst"""
        return f"{currency} {self.unit_price:,.2f}"

    def format_total(self, currency: str = "€") -> str:
        """Formatteer het totaal als tekst"""
        return f"{currency} {self.total:,.2f}"

    def format_quantity(self) -> str:
        """Formatteer de hoeveelheid met eenheid"""
        if self.quantity_type == QuantityType.COUNT:
            # Geen decimalen voor stuks
            return f"{int(self.quantity)} {self.unit_symbol}"
        return f"{self.quantity:,.2f} {self.unit_symbol}"

    @classmethod
    def from_ifc(cls, ifc_cost_value, ifc_quantity=None) -> "CostValue":
        """
        Maak een CostValue van IFC objecten.

        Args:
            ifc_cost_value: IfcCostValue object
            ifc_quantity: Optioneel quantity object

        Returns:
            CostValue instance
        """
        # Extract unit price
        unit_price = 0.0
        if hasattr(ifc_cost_value, "AppliedValue") and ifc_cost_value.AppliedValue:
            applied = ifc_cost_value.AppliedValue
            if hasattr(applied, "wrappedValue"):
                unit_price = float(applied.wrappedValue)
            else:
                try:
                    unit_price = float(applied)
                except (TypeError, ValueError):
                    pass

        # Extract category
        category = ""
        if hasattr(ifc_cost_value, "Category") and ifc_cost_value.Category:
            category = str(ifc_cost_value.Category)

        # Extract quantity
        quantity = 0.0
        quantity_type = QuantityType.COUNT

        if ifc_quantity:
            if hasattr(ifc_quantity, "CountValue") and ifc_quantity.CountValue:
                quantity = float(ifc_quantity.CountValue)
                quantity_type = QuantityType.COUNT
            elif hasattr(ifc_quantity, "LengthValue") and ifc_quantity.LengthValue:
                quantity = float(ifc_quantity.LengthValue)
                quantity_type = QuantityType.LENGTH
            elif hasattr(ifc_quantity, "AreaValue") and ifc_quantity.AreaValue:
                quantity = float(ifc_quantity.AreaValue)
                quantity_type = QuantityType.AREA
            elif hasattr(ifc_quantity, "VolumeValue") and ifc_quantity.VolumeValue:
                quantity = float(ifc_quantity.VolumeValue)
                quantity_type = QuantityType.VOLUME
            elif hasattr(ifc_quantity, "WeightValue") and ifc_quantity.WeightValue:
                quantity = float(ifc_quantity.WeightValue)
                quantity_type = QuantityType.WEIGHT

        return cls(
            unit_price=unit_price,
            quantity=quantity,
            quantity_type=quantity_type,
            category=category,
            ifc_cost_value=ifc_cost_value,
            ifc_quantity=ifc_quantity
        )
