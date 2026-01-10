"""
IFC Handler - Basis lezen/schrijven van IFC bestanden
"""

import ifcopenshell
import ifcopenshell.api
from pathlib import Path
from typing import Optional
from datetime import datetime


class IFCHandler:
    """Handler voor IFC bestandsoperaties"""

    def __init__(self):
        self._ifc_file: Optional[ifcopenshell.file] = None
        self._file_path: Optional[Path] = None
        self._is_modified: bool = False

    @property
    def ifc_file(self) -> Optional[ifcopenshell.file]:
        """Geeft het huidige IFC bestand terug"""
        return self._ifc_file

    @property
    def file_path(self) -> Optional[Path]:
        """Geeft het pad naar het huidige bestand terug"""
        return self._file_path

    @property
    def is_modified(self) -> bool:
        """Geeft aan of het bestand is gewijzigd sinds laatste opslaan"""
        return self._is_modified

    def mark_modified(self):
        """Markeer het bestand als gewijzigd"""
        self._is_modified = True

    def new_file(self, schema: str = "IFC4") -> ifcopenshell.file:
        """
        Maak een nieuw IFC bestand aan voor kostenbegrotingen.

        Args:
            schema: IFC schema versie (standaard IFC4)

        Returns:
            Nieuw IFC bestand
        """
        self._ifc_file = ifcopenshell.file(schema=schema)
        self._file_path = None
        self._is_modified = True

        # Maak basis project structuur
        self._create_project_structure()

        return self._ifc_file

    def _create_project_structure(self):
        """Maak basis IFC project structuur aan"""
        if not self._ifc_file:
            return

        # Maak IfcProject
        project = ifcopenshell.api.run(
            "root.create_entity",
            self._ifc_file,
            ifc_class="IfcProject",
            name="Bouwkosten Begroting"
        )

        # Stel eenheden in (metric)
        ifcopenshell.api.run(
            "unit.assign_unit",
            self._ifc_file,
            length={"is_metric": True, "raw": "METRE"},
            area={"is_metric": True, "raw": "SQUARE_METRE"},
            volume={"is_metric": True, "raw": "CUBIC_METRE"}
        )

        # Maak standaard context
        ifcopenshell.api.run(
            "context.add_context",
            self._ifc_file,
            context_type="Model"
        )

    def open_file(self, file_path: str | Path) -> ifcopenshell.file:
        """
        Open een bestaand IFC bestand.

        Args:
            file_path: Pad naar het IFC bestand

        Returns:
            Geopend IFC bestand

        Raises:
            FileNotFoundError: Als bestand niet bestaat
            Exception: Bij andere fouten tijdens openen
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Bestand niet gevonden: {path}")

        self._ifc_file = ifcopenshell.open(str(path))
        self._file_path = path
        self._is_modified = False

        return self._ifc_file

    def save_file(self, file_path: Optional[str | Path] = None) -> Path:
        """
        Sla het IFC bestand op.

        Args:
            file_path: Optioneel nieuw pad (voor 'opslaan als')

        Returns:
            Pad naar opgeslagen bestand

        Raises:
            ValueError: Als er geen bestand is om op te slaan
        """
        if not self._ifc_file:
            raise ValueError("Geen IFC bestand om op te slaan")

        if file_path:
            self._file_path = Path(file_path)
        elif not self._file_path:
            raise ValueError("Geen bestandspad opgegeven")

        # Zorg ervoor dat het bestand .ifc extensie heeft
        if self._file_path.suffix.lower() != ".ifc":
            self._file_path = self._file_path.with_suffix(".ifc")

        self._ifc_file.write(str(self._file_path))
        self._is_modified = False

        return self._file_path

    def close_file(self):
        """Sluit het huidige bestand"""
        self._ifc_file = None
        self._file_path = None
        self._is_modified = False

    def get_project(self):
        """Haal het IfcProject op uit het bestand"""
        if not self._ifc_file:
            return None
        projects = self._ifc_file.by_type("IfcProject")
        return projects[0] if projects else None

    def get_cost_schedules(self) -> list:
        """Haal alle kostenschema's op uit het bestand"""
        if not self._ifc_file:
            return []
        return self._ifc_file.by_type("IfcCostSchedule")

    def get_all_cost_items(self) -> list:
        """Haal alle kostenposten op uit het bestand"""
        if not self._ifc_file:
            return []
        return self._ifc_file.by_type("IfcCostItem")
