"""
CostItem Model - Representeert een kostenpost (hiërarchisch)
"""

from dataclasses import dataclass, field
from typing import Optional, List, TYPE_CHECKING
from .cost_value import CostValue, QuantityType

if TYPE_CHECKING:
    from .cost_schedule import CostSchedule


@dataclass
class CostItem:
    """
    Representeert een kostenpost in de begroting.
    Kan hiërarchisch genest zijn (hoofdstukken → paragrafen → regels).

    Attributes:
        name: Naam/omschrijving van de post
        html_name: HTML opmaak van de naam (voor vet, italic, kleur, etc.)
        identification: STABU-code van de post (bijv. "01.02.03")
        sfb_code: SFB-codering (bijv. "21.1")
        description: Uitgebreide omschrijving
        is_text_only: Tekstregel zonder hoeveelheid/kosten (voor opmerkingen)
        cost_value: Kostenwaarde (eenheidsprijs en hoeveelheid)
        children: Geneste kostenposten
        parent: Bovenliggende kostenpost
        ifc_cost_item: Referentie naar IFC object
    """
    name: str = ""
    html_name: str = ""  # HTML opmaak van de naam (voor vet, italic, etc.)
    identification: str = ""  # STABU-code
    sfb_code: str = ""  # SFB-codering
    description: str = ""
    is_text_only: bool = False  # Tekstregel zonder hoeveelheid/kosten
    cost_value: CostValue = field(default_factory=CostValue)
    children: List["CostItem"] = field(default_factory=list)
    parent: Optional["CostItem"] = field(default=None, repr=False)
    schedule: Optional["CostSchedule"] = field(default=None, repr=False)
    ifc_cost_item: Optional[object] = field(default=None, repr=False)

    def __post_init__(self):
        """Zet parent referenties voor children"""
        for child in self.children:
            child.parent = self

    @property
    def is_chapter(self) -> bool:
        """Is dit een hoofdstuk (heeft kinderen)?"""
        return len(self.children) > 0

    @property
    def is_leaf(self) -> bool:
        """Is dit een bladpost (geen kinderen)?"""
        return len(self.children) == 0

    @property
    def level(self) -> int:
        """Bepaal het niveau in de hiërarchie (0 = root)"""
        level = 0
        item = self.parent
        while item:
            level += 1
            item = item.parent
        return level

    @property
    def unit_price(self) -> float:
        """Eenheidsprijs van deze post"""
        return self.cost_value.unit_price

    @unit_price.setter
    def unit_price(self, value: float):
        self.cost_value.unit_price = value

    @property
    def quantity(self) -> float:
        """Hoeveelheid van deze post"""
        return self.cost_value.quantity

    @quantity.setter
    def quantity(self, value: float):
        self.cost_value.quantity = value

    @property
    def quantity_type(self) -> QuantityType:
        """Type hoeveelheid"""
        return self.cost_value.quantity_type

    @quantity_type.setter
    def quantity_type(self, value: QuantityType):
        self.cost_value.quantity_type = value

    @property
    def unit_symbol(self) -> str:
        """Eenheidssymbool"""
        return self.cost_value.unit_symbol

    @property
    def subtotal(self) -> float:
        """
        Bereken subtotaal van deze post.
        Voor tekstregels: altijd 0
        Voor bladposten: quantity * unit_price
        Voor hoofdstukken: som van subtotalen van kinderen
        """
        if self.is_text_only:
            return 0.0
        if self.is_leaf:
            return self.cost_value.total
        return sum(child.subtotal for child in self.children)

    @property
    def total(self) -> float:
        """Alias voor subtotal"""
        return self.subtotal

    def add_child(self, child: "CostItem") -> "CostItem":
        """
        Voeg een kind-post toe.

        Args:
            child: De toe te voegen CostItem

        Returns:
            De toegevoegde CostItem
        """
        child.parent = self
        child.schedule = self.schedule
        self.children.append(child)
        return child

    def remove_child(self, child: "CostItem") -> bool:
        """
        Verwijder een kind-post.

        Args:
            child: De te verwijderen CostItem

        Returns:
            True als succesvol, False als niet gevonden
        """
        if child in self.children:
            child.parent = None
            child.schedule = None
            self.children.remove(child)
            return True
        return False

    def insert_child(self, index: int, child: "CostItem") -> "CostItem":
        """
        Voeg een kind-post toe op een specifieke positie.

        Args:
            index: Positie om in te voegen
            child: De toe te voegen CostItem

        Returns:
            De toegevoegde CostItem
        """
        child.parent = self
        child.schedule = self.schedule
        self.children.insert(index, child)
        return child

    def get_child_index(self, child: "CostItem") -> int:
        """
        Haal de index van een kind op.

        Args:
            child: De CostItem om te zoeken

        Returns:
            Index van het kind, of -1 als niet gevonden
        """
        try:
            return self.children.index(child)
        except ValueError:
            return -1

    def move_up(self) -> bool:
        """
        Verplaats dit item één positie omhoog in de parent.

        Returns:
            True als succesvol
        """
        if not self.parent:
            return False
        index = self.parent.get_child_index(self)
        if index <= 0:
            return False
        self.parent.children.remove(self)
        self.parent.children.insert(index - 1, self)
        return True

    def move_down(self) -> bool:
        """
        Verplaats dit item één positie omlaag in de parent.

        Returns:
            True als succesvol
        """
        if not self.parent:
            return False
        index = self.parent.get_child_index(self)
        if index < 0 or index >= len(self.parent.children) - 1:
            return False
        self.parent.children.remove(self)
        self.parent.children.insert(index + 1, self)
        return True

    def get_path(self) -> List["CostItem"]:
        """
        Haal het pad van root naar dit item op.

        Returns:
            Lijst van CostItems van root naar dit item
        """
        path = [self]
        item = self.parent
        while item:
            path.insert(0, item)
            item = item.parent
        return path

    def get_full_identification(self, separator: str = ".") -> str:
        """
        Haal de volledige identificatie op (inclusief parent codes).

        Args:
            separator: Scheidingsteken tussen niveaus

        Returns:
            Volledige identificatiecode
        """
        parts = []
        for item in self.get_path():
            if item.identification:
                parts.append(item.identification)
        return separator.join(parts)

    def find_by_identification(self, identification: str) -> Optional["CostItem"]:
        """
        Zoek een item op identificatie (recursief).

        Args:
            identification: Te zoeken identificatie

        Returns:
            Gevonden CostItem of None
        """
        if self.identification == identification:
            return self
        for child in self.children:
            found = child.find_by_identification(identification)
            if found:
                return found
        return None

    def get_all_descendants(self) -> List["CostItem"]:
        """
        Haal alle nakomelingen op (recursief).

        Returns:
            Lijst van alle nakomeling CostItems
        """
        descendants = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants

    def format_subtotal(self, currency: str = "€") -> str:
        """Formatteer het subtotaal als tekst"""
        return f"{currency} {self.subtotal:,.2f}"

    def copy(self) -> "CostItem":
        """
        Maak een diepe kopie van dit item (zonder parent/schedule referenties).

        Returns:
            Nieuwe CostItem met dezelfde data
        """
        # Kopieer cost_value
        new_cost_value = CostValue(
            unit_price=self.cost_value.unit_price,
            quantity=self.cost_value.quantity,
            quantity_type=self.cost_value.quantity_type
        )

        # Maak nieuwe item
        new_item = CostItem(
            name=self.name,
            html_name=self.html_name,
            identification=self.identification,
            sfb_code=self.sfb_code,
            description=self.description,
            is_text_only=self.is_text_only,
            cost_value=new_cost_value
        )

        # Kopieer children recursief
        for child in self.children:
            child_copy = child.copy()
            new_item.add_child(child_copy)

        return new_item

    @classmethod
    def from_ifc(cls, ifc_cost_item, parent: Optional["CostItem"] = None) -> "CostItem":
        """
        Maak een CostItem van een IFC object.

        Args:
            ifc_cost_item: IfcCostItem object
            parent: Optionele parent CostItem

        Returns:
            CostItem instance
        """
        # Basis attributen
        name = ifc_cost_item.Name or ""
        identification = ifc_cost_item.Identification or ""
        description = ifc_cost_item.Description or ""

        # Cost value
        cost_value = CostValue()

        # Haal cost values op
        if hasattr(ifc_cost_item, "CostValues") and ifc_cost_item.CostValues:
            values = list(ifc_cost_item.CostValues)
            if values:
                # Pak de eerste quantity indien beschikbaar
                ifc_quantity = None
                if hasattr(ifc_cost_item, "CostQuantities") and ifc_cost_item.CostQuantities:
                    quantities = list(ifc_cost_item.CostQuantities)
                    if quantities:
                        ifc_quantity = quantities[0]
                cost_value = CostValue.from_ifc(values[0], ifc_quantity)

        return cls(
            name=name,
            identification=identification,
            description=description,
            cost_value=cost_value,
            parent=parent,
            ifc_cost_item=ifc_cost_item
        )
