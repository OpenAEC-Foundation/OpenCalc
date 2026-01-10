"""
CostSchedule Model - Representeert een kostenbegroting
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import date
from enum import Enum

from .cost_item import CostItem


class ScheduleType(Enum):
    """Types kostenschema's"""
    BUDGET = "BUDGET"
    COSTPLAN = "COSTPLAN"
    ESTIMATE = "ESTIMATE"
    TENDER = "TENDER"
    PRICEDBILLOFQUANTITIES = "PRICEDBILLOFQUANTITIES"
    UNPRICEDBILLOFQUANTITIES = "UNPRICEDBILLOFQUANTITIES"
    SCHEDULEOFRATES = "SCHEDULEOFRATES"


class ScheduleStatus(Enum):
    """Status van een kostenschema"""
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    SUBMITTED = "SUBMITTED"
    REJECTED = "REJECTED"


@dataclass
class CostSchedule:
    """
    Representeert een volledige kostenbegroting.

    Attributes:
        name: Naam van de begroting
        description: Omschrijving
        schedule_type: Type begroting
        status: Status van de begroting
        created_date: Aanmaakdatum
        update_date: Laatste wijzigingsdatum
        submitted_on: Datum van indiening
        items: Lijst van root kostenposten
        vat_rate: BTW percentage (standaard 21%)
        ifc_cost_schedule: Referentie naar IFC object
    """
    name: str = "Nieuwe Begroting"
    description: str = ""
    schedule_type: ScheduleType = ScheduleType.BUDGET
    status: ScheduleStatus = ScheduleStatus.DRAFT
    created_date: Optional[date] = field(default_factory=date.today)
    update_date: Optional[date] = None
    submitted_on: Optional[date] = None
    items: List[CostItem] = field(default_factory=list)
    vat_rate: float = 21.0  # BTW percentage
    ifc_cost_schedule: Optional[object] = field(default=None, repr=False)

    def __post_init__(self):
        """Zet schedule referenties voor items"""
        for item in self.items:
            item.schedule = self
            self._set_schedule_recursive(item)

    def _set_schedule_recursive(self, item: CostItem):
        """Zet schedule referentie recursief"""
        item.schedule = self
        for child in item.children:
            self._set_schedule_recursive(child)

    @property
    def subtotal(self) -> float:
        """Subtotaal exclusief BTW"""
        return sum(item.subtotal for item in self.items)

    @property
    def vat_amount(self) -> float:
        """BTW bedrag"""
        return self.subtotal * (self.vat_rate / 100)

    @property
    def total(self) -> float:
        """Totaal inclusief BTW"""
        return self.subtotal + self.vat_amount

    @property
    def item_count(self) -> int:
        """Totaal aantal items (inclusief geneste)"""
        count = 0
        for item in self.items:
            count += 1 + len(item.get_all_descendants())
        return count

    @property
    def chapter_count(self) -> int:
        """Aantal hoofdstukken (root items)"""
        return len(self.items)

    def add_item(self, item: CostItem) -> CostItem:
        """
        Voeg een root kostenpost toe.

        Args:
            item: De toe te voegen CostItem

        Returns:
            De toegevoegde CostItem
        """
        item.schedule = self
        item.parent = None
        self.items.append(item)
        return item

    def remove_item(self, item: CostItem) -> bool:
        """
        Verwijder een root kostenpost.

        Args:
            item: De te verwijderen CostItem

        Returns:
            True als succesvol
        """
        if item in self.items:
            item.schedule = None
            self.items.remove(item)
            return True
        return False

    def insert_item(self, index: int, item: CostItem) -> CostItem:
        """
        Voeg een root kostenpost toe op een specifieke positie.

        Args:
            index: Positie om in te voegen
            item: De toe te voegen CostItem

        Returns:
            De toegevoegde CostItem
        """
        item.schedule = self
        item.parent = None
        self.items.insert(index, item)
        return item

    def get_item_index(self, item: CostItem) -> int:
        """
        Haal de index van een root item op.

        Args:
            item: De CostItem om te zoeken

        Returns:
            Index van het item, of -1 als niet gevonden
        """
        try:
            return self.items.index(item)
        except ValueError:
            return -1

    def find_by_identification(self, identification: str) -> Optional[CostItem]:
        """
        Zoek een item op identificatie.

        Args:
            identification: Te zoeken identificatie

        Returns:
            Gevonden CostItem of None
        """
        for item in self.items:
            found = item.find_by_identification(identification)
            if found:
                return found
        return None

    def get_all_items(self) -> List[CostItem]:
        """
        Haal alle items op (platte lijst).

        Returns:
            Lijst van alle CostItems
        """
        all_items = []
        for item in self.items:
            all_items.append(item)
            all_items.extend(item.get_all_descendants())
        return all_items

    def get_items_at_level(self, level: int) -> List[CostItem]:
        """
        Haal alle items op een bepaald niveau.

        Args:
            level: Niveau (0 = root items)

        Returns:
            Lijst van CostItems op dat niveau
        """
        return [item for item in self.get_all_items() if item.level == level]

    def format_subtotal(self, currency: str = "€") -> str:
        """Formatteer het subtotaal als tekst"""
        return f"{currency} {self.subtotal:,.2f}"

    def format_vat(self, currency: str = "€") -> str:
        """Formatteer het BTW bedrag als tekst"""
        return f"{currency} {self.vat_amount:,.2f}"

    def format_total(self, currency: str = "€") -> str:
        """Formatteer het totaal als tekst"""
        return f"{currency} {self.total:,.2f}"

    def create_chapter(
        self,
        name: str,
        identification: str = "",
        description: str = ""
    ) -> CostItem:
        """
        Maak een nieuw hoofdstuk aan.

        Args:
            name: Naam van het hoofdstuk
            identification: Code (bijv. "01")
            description: Omschrijving

        Returns:
            Het aangemaakte CostItem
        """
        # Auto-genereer identificatie als niet opgegeven
        if not identification:
            identification = f"{len(self.items) + 1:02d}"

        chapter = CostItem(
            name=name,
            identification=identification,
            description=description
        )
        return self.add_item(chapter)

    def mark_modified(self):
        """Markeer de begroting als gewijzigd"""
        self.update_date = date.today()

    @classmethod
    def from_ifc(cls, ifc_cost_schedule) -> "CostSchedule":
        """
        Maak een CostSchedule van een IFC object.

        Args:
            ifc_cost_schedule: IfcCostSchedule object

        Returns:
            CostSchedule instance
        """
        # Basis attributen
        name = ifc_cost_schedule.Name or "Onbekende Begroting"
        description = ifc_cost_schedule.Description or ""

        # Type
        schedule_type = ScheduleType.BUDGET
        if hasattr(ifc_cost_schedule, "PredefinedType") and ifc_cost_schedule.PredefinedType:
            try:
                schedule_type = ScheduleType(ifc_cost_schedule.PredefinedType)
            except ValueError:
                pass

        # Status
        status = ScheduleStatus.DRAFT
        if hasattr(ifc_cost_schedule, "Status") and ifc_cost_schedule.Status:
            try:
                status = ScheduleStatus(ifc_cost_schedule.Status.upper())
            except ValueError:
                pass

        schedule = cls(
            name=name,
            description=description,
            schedule_type=schedule_type,
            status=status,
            ifc_cost_schedule=ifc_cost_schedule
        )

        return schedule
