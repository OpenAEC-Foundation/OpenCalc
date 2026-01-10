"""
Cost API - Wrapper voor ifcopenshell.api.cost
Biedt een high-level interface voor het werken met IFC kostenschema's
"""

import ifcopenshell
import ifcopenshell.api
from typing import Optional, List, Dict, Any


class CostAPI:
    """Wrapper klasse voor IfcOpenShell cost API"""

    def __init__(self, ifc_file: ifcopenshell.file):
        """
        Initialiseer de Cost API wrapper.

        Args:
            ifc_file: Het IFC bestand om mee te werken
        """
        self._ifc_file = ifc_file

    @property
    def ifc_file(self) -> ifcopenshell.file:
        return self._ifc_file

    @ifc_file.setter
    def ifc_file(self, value: ifcopenshell.file):
        self._ifc_file = value

    # =========================================================================
    # COST SCHEDULE OPERATIES
    # =========================================================================

    def add_cost_schedule(
        self,
        name: str,
        predefined_type: str = "BUDGET",
        status: Optional[str] = None,
        submitted_on: Optional[str] = None,
        update_date: Optional[str] = None
    ):
        """
        Maak een nieuw kostenschema (begroting) aan.

        Args:
            name: Naam van het kostenschema
            predefined_type: Type schema (BUDGET, COSTPLAN, ESTIMATE, etc.)
            status: Status van het schema
            submitted_on: Datum van indiening
            update_date: Laatste update datum

        Returns:
            Het aangemaakte IfcCostSchedule object
        """
        schedule = ifcopenshell.api.run(
            "cost.add_cost_schedule",
            self._ifc_file,
            name=name,
            predefined_type=predefined_type
        )

        # Stel optionele attributen in
        if status:
            schedule.Status = status
        if submitted_on:
            schedule.SubmittedOn = submitted_on
        if update_date:
            schedule.UpdateDate = update_date

        return schedule

    def edit_cost_schedule(
        self,
        cost_schedule,
        attributes: Dict[str, Any]
    ):
        """
        Bewerk een bestaand kostenschema.

        Args:
            cost_schedule: Het te bewerken IfcCostSchedule
            attributes: Dictionary met attributen om te wijzigen
        """
        ifcopenshell.api.run(
            "cost.edit_cost_schedule",
            self._ifc_file,
            cost_schedule=cost_schedule,
            attributes=attributes
        )

    def remove_cost_schedule(self, cost_schedule):
        """
        Verwijder een kostenschema.

        Args:
            cost_schedule: Het te verwijderen IfcCostSchedule
        """
        ifcopenshell.api.run(
            "cost.remove_cost_schedule",
            self._ifc_file,
            cost_schedule=cost_schedule
        )

    def copy_cost_schedule(self, cost_schedule):
        """
        Kopieer een kostenschema inclusief alle items.

        Args:
            cost_schedule: Het te kopiëren IfcCostSchedule

        Returns:
            Het gekopieerde IfcCostSchedule
        """
        return ifcopenshell.api.run(
            "cost.copy_cost_schedule",
            self._ifc_file,
            cost_schedule=cost_schedule
        )

    # =========================================================================
    # COST ITEM OPERATIES
    # =========================================================================

    def add_cost_item(
        self,
        cost_schedule=None,
        cost_item=None,
        name: str = "",
        identification: str = ""
    ):
        """
        Voeg een kostenpost toe aan een schema of als sub-item.

        Args:
            cost_schedule: Het bovenliggende kostenschema (voor root items)
            cost_item: Het bovenliggende cost item (voor geneste items)
            name: Naam van de kostenpost
            identification: Code/identificatie van de post

        Returns:
            Het aangemaakte IfcCostItem

        Raises:
            ValueError: Als noch cost_schedule noch cost_item is opgegeven
        """
        if not cost_schedule and not cost_item:
            raise ValueError("Geef een cost_schedule of cost_item op als parent")

        item = ifcopenshell.api.run(
            "cost.add_cost_item",
            self._ifc_file,
            cost_schedule=cost_schedule,
            cost_item=cost_item
        )

        # Stel naam en identificatie in
        if name:
            item.Name = name
        if identification:
            item.Identification = identification

        return item

    def edit_cost_item(
        self,
        cost_item,
        attributes: Dict[str, Any]
    ):
        """
        Bewerk een bestaande kostenpost.

        Args:
            cost_item: Het te bewerken IfcCostItem
            attributes: Dictionary met attributen om te wijzigen
                       (Name, Description, Identification, etc.)
        """
        ifcopenshell.api.run(
            "cost.edit_cost_item",
            self._ifc_file,
            cost_item=cost_item,
            attributes=attributes
        )

    def remove_cost_item(self, cost_item):
        """
        Verwijder een kostenpost.

        Args:
            cost_item: Het te verwijderen IfcCostItem
        """
        ifcopenshell.api.run(
            "cost.remove_cost_item",
            self._ifc_file,
            cost_item=cost_item
        )

    def copy_cost_item(self, cost_item):
        """
        Kopieer een kostenpost inclusief sub-items.

        Args:
            cost_item: Het te kopiëren IfcCostItem

        Returns:
            Het gekopieerde IfcCostItem
        """
        return ifcopenshell.api.run(
            "cost.copy_cost_item",
            self._ifc_file,
            cost_item=cost_item
        )

    def get_nested_cost_items(self, cost_item) -> List:
        """
        Haal geneste kostenposten op voor een item.

        Args:
            cost_item: Het parent IfcCostItem

        Returns:
            Lijst van geneste IfcCostItems
        """
        nested = []
        if hasattr(cost_item, "IsNestedBy") and cost_item.IsNestedBy:
            for rel in cost_item.IsNestedBy:
                if hasattr(rel, "RelatedObjects"):
                    nested.extend(rel.RelatedObjects)
        return nested

    def get_root_cost_items(self, cost_schedule) -> List:
        """
        Haal root kostenposten op voor een kostenschema.

        Args:
            cost_schedule: Het IfcCostSchedule

        Returns:
            Lijst van root IfcCostItems
        """
        items = []
        if hasattr(cost_schedule, "Controls") and cost_schedule.Controls:
            for rel in cost_schedule.Controls:
                if hasattr(rel, "RelatedObjects"):
                    items.extend([obj for obj in rel.RelatedObjects
                                  if obj.is_a("IfcCostItem")])
        return items

    # =========================================================================
    # COST VALUE OPERATIES
    # =========================================================================

    def add_cost_value(self, parent):
        """
        Voeg een kostenwaarde toe aan een kostenpost.

        Args:
            parent: Het parent IfcCostItem

        Returns:
            Het aangemaakte IfcCostValue
        """
        return ifcopenshell.api.run(
            "cost.add_cost_value",
            self._ifc_file,
            parent=parent
        )

    def edit_cost_value(
        self,
        cost_value,
        attributes: Dict[str, Any]
    ):
        """
        Bewerk een kostenwaarde.

        Args:
            cost_value: Het te bewerken IfcCostValue
            attributes: Dictionary met attributen
                       (AppliedValue, UnitBasis, Category, etc.)
        """
        ifcopenshell.api.run(
            "cost.edit_cost_value",
            self._ifc_file,
            cost_value=cost_value,
            attributes=attributes
        )

    def remove_cost_value(self, parent, cost_value):
        """
        Verwijder een kostenwaarde.

        Args:
            parent: Het parent IfcCostItem
            cost_value: Het te verwijderen IfcCostValue
        """
        ifcopenshell.api.run(
            "cost.remove_cost_value",
            self._ifc_file,
            parent=parent,
            cost_value=cost_value
        )

    # =========================================================================
    # QUANTITY OPERATIES
    # =========================================================================

    def add_cost_item_quantity(
        self,
        cost_item,
        ifc_class: str = "IfcQuantityCount"
    ):
        """
        Voeg een hoeveelheid toe aan een kostenpost.

        Args:
            cost_item: Het IfcCostItem
            ifc_class: Type hoeveelheid:
                      - IfcQuantityCount (stuks)
                      - IfcQuantityLength (m)
                      - IfcQuantityArea (m²)
                      - IfcQuantityVolume (m³)
                      - IfcQuantityWeight (kg)
                      - IfcQuantityTime (tijd)
                      - IfcQuantityNumber (generiek nummer)

        Returns:
            Het aangemaakte quantity object
        """
        return ifcopenshell.api.run(
            "cost.add_cost_item_quantity",
            self._ifc_file,
            cost_item=cost_item,
            ifc_class=ifc_class
        )

    def edit_cost_item_quantity(
        self,
        physical_quantity,
        attributes: Dict[str, Any]
    ):
        """
        Bewerk een hoeveelheid.

        Args:
            physical_quantity: Het te bewerken quantity object
            attributes: Dictionary met attributen
                       (Name, CountValue, LengthValue, AreaValue, etc.)
        """
        ifcopenshell.api.run(
            "cost.edit_cost_item_quantity",
            self._ifc_file,
            physical_quantity=physical_quantity,
            attributes=attributes
        )

    def remove_cost_item_quantity(self, cost_item, physical_quantity):
        """
        Verwijder een hoeveelheid van een kostenpost.

        Args:
            cost_item: Het IfcCostItem
            physical_quantity: Het te verwijderen quantity object
        """
        ifcopenshell.api.run(
            "cost.remove_cost_item_quantity",
            self._ifc_file,
            cost_item=cost_item,
            physical_quantity=physical_quantity
        )

    def assign_cost_item_quantity(
        self,
        cost_item,
        products: List,
        prop_name: str
    ):
        """
        Koppel hoeveelheden van IFC producten aan een kostenpost.

        Args:
            cost_item: Het IfcCostItem
            products: Lijst van IFC producten (muren, deuren, etc.)
            prop_name: Naam van de property (bijv. "NetVolume", "GrossArea")
        """
        ifcopenshell.api.run(
            "cost.assign_cost_item_quantity",
            self._ifc_file,
            cost_item=cost_item,
            products=products,
            prop_name=prop_name
        )

    # =========================================================================
    # HELPER METHODES
    # =========================================================================

    def get_cost_item_quantities(self, cost_item) -> List:
        """
        Haal alle hoeveelheden op voor een kostenpost.

        Args:
            cost_item: Het IfcCostItem

        Returns:
            Lijst van quantity objecten
        """
        if hasattr(cost_item, "CostQuantities") and cost_item.CostQuantities:
            return list(cost_item.CostQuantities)
        return []

    def get_cost_item_values(self, cost_item) -> List:
        """
        Haal alle kostenwaarden op voor een kostenpost.

        Args:
            cost_item: Het IfcCostItem

        Returns:
            Lijst van IfcCostValue objecten
        """
        if hasattr(cost_item, "CostValues") and cost_item.CostValues:
            return list(cost_item.CostValues)
        return []

    def calculate_total(self, cost_item) -> float:
        """
        Bereken het totaal voor een kostenpost.
        Totaal = som(quantities) * som(values)

        Args:
            cost_item: Het IfcCostItem

        Returns:
            Het berekende totaal
        """
        quantities = self.get_cost_item_quantities(cost_item)
        values = self.get_cost_item_values(cost_item)

        # Som van hoeveelheden
        qty_sum = 0.0
        for qty in quantities:
            if hasattr(qty, "CountValue") and qty.CountValue:
                qty_sum += float(qty.CountValue)
            elif hasattr(qty, "LengthValue") and qty.LengthValue:
                qty_sum += float(qty.LengthValue)
            elif hasattr(qty, "AreaValue") and qty.AreaValue:
                qty_sum += float(qty.AreaValue)
            elif hasattr(qty, "VolumeValue") and qty.VolumeValue:
                qty_sum += float(qty.VolumeValue)
            elif hasattr(qty, "WeightValue") and qty.WeightValue:
                qty_sum += float(qty.WeightValue)

        # Som van waarden (eenheidsprijzen)
        value_sum = 0.0
        for val in values:
            if hasattr(val, "AppliedValue") and val.AppliedValue:
                applied = val.AppliedValue
                if hasattr(applied, "wrappedValue"):
                    value_sum += float(applied.wrappedValue)
                else:
                    try:
                        value_sum += float(applied)
                    except (TypeError, ValueError):
                        pass

        return qty_sum * value_sum if qty_sum > 0 and value_sum > 0 else 0.0

    # =========================================================================
    # HTML NAME OPERATIES
    # =========================================================================

    def set_html_name(self, cost_item, html_name: str):
        """
        Sla de HTML opmaak van de naam op als property van een kostenpost.

        Args:
            cost_item: Het IfcCostItem
            html_name: De HTML opmaak om op te slaan
        """
        if not html_name:
            return

        # Zoek of maak PropertySet "Pset_CostFormatting"
        pset = self._get_or_create_pset(cost_item, "Pset_CostFormatting")

        # Voeg of update de HtmlName property
        self._set_pset_property(pset, "HtmlName", html_name)

    def get_html_name(self, cost_item) -> str:
        """
        Haal de HTML opmaak van de naam op uit de properties van een kostenpost.

        Args:
            cost_item: Het IfcCostItem

        Returns:
            De HTML opmaak of lege string
        """
        # Zoek PropertySet "Pset_CostFormatting"
        if hasattr(cost_item, "IsDefinedBy") and cost_item.IsDefinedBy:
            for rel in cost_item.IsDefinedBy:
                if rel.is_a("IfcRelDefinesByProperties"):
                    pset = rel.RelatingPropertyDefinition
                    if pset.is_a("IfcPropertySet") and pset.Name == "Pset_CostFormatting":
                        for prop in pset.HasProperties:
                            if prop.Name == "HtmlName" and hasattr(prop, "NominalValue"):
                                if prop.NominalValue:
                                    return str(prop.NominalValue.wrappedValue)
        return ""

    def set_is_text_only(self, cost_item, is_text_only: bool):
        """
        Sla de tekstregel-markering op als property van een kostenpost.

        Args:
            cost_item: Het IfcCostItem
            is_text_only: True als dit een tekstregel is zonder kosten
        """
        # Zoek of maak PropertySet "Pset_CostFormatting"
        pset = self._get_or_create_pset(cost_item, "Pset_CostFormatting")

        # Voeg of update de IsTextOnly property
        self._set_pset_property(pset, "IsTextOnly", "true" if is_text_only else "false")

    def get_is_text_only(self, cost_item) -> bool:
        """
        Haal de tekstregel-markering op uit de properties van een kostenpost.

        Args:
            cost_item: Het IfcCostItem

        Returns:
            True als dit een tekstregel is
        """
        # Zoek PropertySet "Pset_CostFormatting"
        if hasattr(cost_item, "IsDefinedBy") and cost_item.IsDefinedBy:
            for rel in cost_item.IsDefinedBy:
                if rel.is_a("IfcRelDefinesByProperties"):
                    pset = rel.RelatingPropertyDefinition
                    if pset.is_a("IfcPropertySet") and pset.Name == "Pset_CostFormatting":
                        for prop in pset.HasProperties:
                            if prop.Name == "IsTextOnly" and hasattr(prop, "NominalValue"):
                                if prop.NominalValue:
                                    return str(prop.NominalValue.wrappedValue).lower() == "true"
        return False

    # =========================================================================
    # SFB CODE OPERATIES
    # =========================================================================

    def set_sfb_code(self, cost_item, sfb_code: str):
        """
        Sla de SFB-code op als property van een kostenpost.

        Args:
            cost_item: Het IfcCostItem
            sfb_code: De SFB-code om op te slaan
        """
        if not sfb_code:
            return

        # Zoek of maak PropertySet "Pset_CostClassification"
        pset = self._get_or_create_pset(cost_item, "Pset_CostClassification")

        # Voeg of update de SFB_Code property
        self._set_pset_property(pset, "SFB_Code", sfb_code)

    def get_sfb_code(self, cost_item) -> str:
        """
        Haal de SFB-code op uit de properties van een kostenpost.

        Args:
            cost_item: Het IfcCostItem

        Returns:
            De SFB-code of lege string
        """
        # Zoek PropertySet "Pset_CostClassification"
        if hasattr(cost_item, "IsDefinedBy") and cost_item.IsDefinedBy:
            for rel in cost_item.IsDefinedBy:
                if rel.is_a("IfcRelDefinesByProperties"):
                    pset = rel.RelatingPropertyDefinition
                    if pset.is_a("IfcPropertySet") and pset.Name == "Pset_CostClassification":
                        for prop in pset.HasProperties:
                            if prop.Name == "SFB_Code" and hasattr(prop, "NominalValue"):
                                if prop.NominalValue:
                                    return str(prop.NominalValue.wrappedValue)
        return ""

    def _get_or_create_pset(self, element, pset_name: str):
        """
        Haal een PropertySet op of maak een nieuwe aan.

        Args:
            element: Het IFC element
            pset_name: Naam van de PropertySet

        Returns:
            De PropertySet
        """
        # Zoek bestaande pset
        if hasattr(element, "IsDefinedBy") and element.IsDefinedBy:
            for rel in element.IsDefinedBy:
                if rel.is_a("IfcRelDefinesByProperties"):
                    pset = rel.RelatingPropertyDefinition
                    if pset.is_a("IfcPropertySet") and pset.Name == pset_name:
                        return pset

        # Maak nieuwe pset
        pset = ifcopenshell.api.run(
            "pset.add_pset",
            self._ifc_file,
            product=element,
            name=pset_name
        )
        return pset

    def _set_pset_property(self, pset, prop_name: str, value: str):
        """
        Stel een property waarde in op een PropertySet.

        Args:
            pset: De IfcPropertySet
            prop_name: Naam van de property
            value: Waarde om op te slaan
        """
        ifcopenshell.api.run(
            "pset.edit_pset",
            self._ifc_file,
            pset=pset,
            properties={prop_name: value}
        )

    # =========================================================================
    # PROJECT DATA OPERATIES
    # =========================================================================

    def save_project_data(self, project_data: Dict[str, Any]):
        """
        Sla projectgegevens op in het IFC bestand.
        Gebruikt PropertySets op het IfcProject object.

        Args:
            project_data: Dictionary met projectgegevens
        """
        # Haal IfcProject op
        projects = self._ifc_file.by_type("IfcProject")
        if not projects:
            return

        project = projects[0]

        # Update projectnaam
        if project_data.get("project_name"):
            project.Name = project_data["project_name"]

        if project_data.get("project_description"):
            project.Description = project_data["project_description"]

        # Sla extra projectgegevens op in PropertySet
        project_pset = self._get_or_create_pset(project, "Pset_ProjectInfo")
        ifcopenshell.api.run(
            "pset.edit_pset",
            self._ifc_file,
            pset=project_pset,
            properties={
                "ProjectNumber": project_data.get("project_number", ""),
                "ProjectLocation": project_data.get("project_location", ""),
                "ProjectDate": project_data.get("project_date", ""),
            }
        )

        # Sla klantgegevens op in PropertySet
        client_pset = self._get_or_create_pset(project, "Pset_ClientInfo")
        ifcopenshell.api.run(
            "pset.edit_pset",
            self._ifc_file,
            pset=client_pset,
            properties={
                "ClientName": project_data.get("client_name", ""),
                "ClientAddress": project_data.get("client_address", ""),
                "ClientPostal": project_data.get("client_postal", ""),
                "ClientContact": project_data.get("client_contact", ""),
                "ClientPhone": project_data.get("client_phone", ""),
                "ClientEmail": project_data.get("client_email", ""),
            }
        )

        # Sla aannemergegevens op in PropertySet
        contractor_pset = self._get_or_create_pset(project, "Pset_ContractorInfo")
        ifcopenshell.api.run(
            "pset.edit_pset",
            self._ifc_file,
            pset=contractor_pset,
            properties={
                "ContractorName": project_data.get("contractor_name", ""),
                "ContractorAddress": project_data.get("contractor_address", ""),
                "ContractorPostal": project_data.get("contractor_postal", ""),
                "ContractorPhone": project_data.get("contractor_phone", ""),
                "ContractorEmail": project_data.get("contractor_email", ""),
                "ContractorKvK": project_data.get("contractor_kvk", ""),
            }
        )

    def load_project_data(self) -> Dict[str, Any]:
        """
        Laad projectgegevens uit het IFC bestand.

        Returns:
            Dictionary met projectgegevens
        """
        project_data = {}

        # Haal IfcProject op
        projects = self._ifc_file.by_type("IfcProject")
        if not projects:
            return project_data

        project = projects[0]

        # Haal projectnaam en beschrijving
        project_data["project_name"] = project.Name or ""
        project_data["project_description"] = project.Description or ""

        # Haal PropertySets op
        if hasattr(project, "IsDefinedBy") and project.IsDefinedBy:
            for rel in project.IsDefinedBy:
                if rel.is_a("IfcRelDefinesByProperties"):
                    pset = rel.RelatingPropertyDefinition
                    if not pset.is_a("IfcPropertySet"):
                        continue

                    pset_name = pset.Name
                    props = {}

                    for prop in pset.HasProperties:
                        if hasattr(prop, "NominalValue") and prop.NominalValue:
                            props[prop.Name] = str(prop.NominalValue.wrappedValue)

                    if pset_name == "Pset_ProjectInfo":
                        project_data["project_number"] = props.get("ProjectNumber", "")
                        project_data["project_location"] = props.get("ProjectLocation", "")
                        project_data["project_date"] = props.get("ProjectDate", "")

                    elif pset_name == "Pset_ClientInfo":
                        project_data["client_name"] = props.get("ClientName", "")
                        project_data["client_address"] = props.get("ClientAddress", "")
                        project_data["client_postal"] = props.get("ClientPostal", "")
                        project_data["client_contact"] = props.get("ClientContact", "")
                        project_data["client_phone"] = props.get("ClientPhone", "")
                        project_data["client_email"] = props.get("ClientEmail", "")

                    elif pset_name == "Pset_ContractorInfo":
                        project_data["contractor_name"] = props.get("ContractorName", "")
                        project_data["contractor_address"] = props.get("ContractorAddress", "")
                        project_data["contractor_postal"] = props.get("ContractorPostal", "")
                        project_data["contractor_phone"] = props.get("ContractorPhone", "")
                        project_data["contractor_email"] = props.get("ContractorEmail", "")
                        project_data["contractor_kvk"] = props.get("ContractorKvK", "")

        return project_data
