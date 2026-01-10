"""
CostTableView - Tabelweergave voor kostenregels met inklapbare hoofdstukken

Geïnspireerd door WpCalc en andere Nederlandse begrotingssoftware.
Gebruikt native Qt TreeView functionaliteit voor expand/collapse.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QHeaderView,
    QAbstractItemView, QStyledItemDelegate, QDoubleSpinBox,
    QMenu, QLabel, QFrame, QToolButton, QSizePolicy, QDialog,
    QLineEdit, QListWidget, QListWidgetItem, QDialogButtonBox,
    QPushButton
)
from PySide6.QtCore import (
    Qt, Signal, QModelIndex, QLocale, QSize, QEvent
)
from PySide6.QtGui import (
    QAction, QColor, QBrush, QFont, QStandardItemModel, QStandardItem
)

from typing import Optional
from ..models import CostSchedule, CostItem
from ..models.cost_value import QuantityType
from .icons import IconProvider
from pathlib import Path


# Custom role voor CostItem data
COST_ITEM_ROLE = Qt.UserRole + 1

# STABU codes database (basis set)
STABU_CODES = [
    ("00", "Algemeen"),
    ("01", "Grondwerk"),
    ("02", "Buitenriolering en drainage"),
    ("03", "Terreinverhardingen"),
    ("04", "Terreininrichting"),
    ("05", "Bouwrijp maken"),
    ("10", "Stut- en sloopwerk"),
    ("11", "Grondwerk en bemaling"),
    ("12", "Betonwerk"),
    ("13", "Metselwerk"),
    ("14", "Vooraf vervaardigde steenachtige elementen"),
    ("15", "Stukadoorwerk"),
    ("16", "Tegelwerk"),
    ("17", "Dekvloeren en gietvloeren"),
    ("20", "Metaalconstructiewerk"),
    ("21", "Smeedwerk"),
    ("22", "Metalen trappen en balustraden"),
    ("23", "Metalen kozijnen, ramen en deuren"),
    ("24", "Metalen gevelbekleding"),
    ("25", "Metalen dakbedekkingen"),
    ("30", "Timmerwerk"),
    ("31", "Houten trappen en balustraden"),
    ("32", "Houten kozijnen, ramen en deuren"),
    ("33", "Systeemwanden"),
    ("34", "Systeemplafonds"),
    ("35", "Houten vloeren"),
    ("36", "Houten gevelbekleding"),
    ("37", "Dakconstructies hout"),
    ("40", "Glas, kunststof, isolatie"),
    ("41", "Glaswerk"),
    ("42", "Kunststofwerk"),
    ("43", "Isolatiewerk"),
    ("44", "Dakbedekkingen"),
    ("45", "Gevelbeplatingen"),
    ("50", "Stucadoorwerk"),
    ("51", "Tegelwerk"),
    ("52", "Dekvloeren"),
    ("53", "Natuursteen"),
    ("54", "Binnenwandafwerking"),
    ("55", "Plafondafwerking"),
    ("56", "Vloerafwerking"),
    ("60", "Schilderwerk"),
    ("61", "Behangwerk"),
    ("62", "Binnenzonwering"),
    ("63", "Buitenzonwering"),
    ("70", "Werktuigbouwkundige installaties"),
    ("71", "Verwarmingsinstallaties"),
    ("72", "Luchtbehandeling"),
    ("73", "Koeling"),
    ("74", "Sanitair"),
    ("75", "Brandbeveiliging"),
    ("76", "Transportinstallaties"),
    ("80", "Elektrotechnische installaties"),
    ("81", "Aardingsinstallaties"),
    ("82", "Laagspanning"),
    ("83", "Verlichting"),
    ("84", "Communicatie"),
    ("85", "Beveiliging"),
    ("90", "Vaste inrichtingen"),
    ("91", "Keukeninrichting"),
    ("92", "Sanitaire inrichting"),
    ("93", "Vaste kasten en bergingen"),
]

# Mapping van STABU codes naar SFB codes (voor auto-populate)
STABU_TO_SFB_MAPPING = {
    # Algemeen / Bouwplaats
    "00": "00",
    "01": "01",
    "02": "03",
    "03": "04",
    "04": "02",
    "05": "00",
    # Ruwbouw
    "10": "17",
    "11": "11",
    "12": "16",
    "13": "21",
    "14": "17",
    "15": "42",
    "16": "43",
    "17": "43",
    # Metaal
    "20": "16.1",
    "21": "16.1",
    "22": "34",
    "23": "31",
    "24": "41",
    "25": "27",
    # Hout
    "30": "13",
    "31": "34",
    "32": "32",
    "33": "22",
    "34": "45",
    "35": "23",
    "36": "41",
    "37": "13.1",
    # Glas/Isolatie
    "40": "31.3",
    "41": "31.3",
    "42": "31.1",
    "43": "27.1",
    "44": "27.2",
    "45": "41",
    # Afwerking
    "50": "42.1",
    "51": "42.2",
    "52": "43.1",
    "53": "43",
    "54": "42",
    "55": "45",
    "56": "43",
    # Schilder
    "60": "42.3",
    "61": "42",
    "62": "48",
    "63": "48",
    # Installaties
    "70": "5-",
    "71": "55",
    "72": "56",
    "73": "55",
    "74": "53",
    "75": "65",
    "76": "59",
    # Elektra
    "80": "57",
    "81": "57",
    "82": "57",
    "83": "57.5",
    "84": "58",
    "85": "64",
    # Vaste inrichting
    "90": "7-",
    "91": "72",
    "92": "71",
    "93": "73",
}


def get_sfb_for_stabu(stabu_code: str) -> str:
    """Haal SFB-code op voor een STABU-code"""
    if not stabu_code:
        return ""

    # Probeer eerst exacte match
    if stabu_code in STABU_TO_SFB_MAPPING:
        return STABU_TO_SFB_MAPPING[stabu_code]

    # Probeer eerste 2 karakters (hoofdcategorie)
    if len(stabu_code) >= 2:
        main_code = stabu_code[:2]
        if main_code in STABU_TO_SFB_MAPPING:
            return STABU_TO_SFB_MAPPING[main_code]

    return ""


# SFB codes database (NL/SfB classificatie) - uitgebreid
SFB_CODES = [
    # 0- Terrein en bouwplaats
    ("0-", "Terreinen en bouwplaats"),
    ("00", "Bouwplaatsvoorzieningen"),
    ("00.1", "Bouwplaatsinrichting"),
    ("00.2", "Uitzetten en maatvoering"),
    ("00.3", "Bouwplaatsbeveiliging"),
    ("00.5", "Bouwstroom en -water"),
    ("01", "Grondwerken"),
    ("02", "Tuinaanleg"),
    ("03", "Riolering en drainage"),
    ("04", "Terreinverhardingen"),
    ("04.1", "Bestrating oprit"),
    ("04.2", "Bestrating terras"),
    # 1- Ruwbouw draagstructuur
    ("1-", "Ruwbouw, draagstructuur"),
    ("11", "Funderingen"),
    ("11.1", "Funderingsstroken"),
    ("11.2", "Funderingsbalken"),
    ("12", "Verdiepingsvloeren"),
    ("12.1", "Kanaalplaatvloeren"),
    ("12.2", "Druklagen"),
    ("13", "Daken, draagconstructie"),
    ("13.1", "Dakconstructie hout"),
    ("14", "Trappen, hellingen"),
    ("14.1", "Trap prefab beton"),
    ("14.2", "Trapafwerking"),
    ("16", "Hoofddraagconstructie"),
    ("16.1", "Staalconstructie"),
    ("17", "Ruwbouwelementen"),
    # 2- Ruwbouw omhulling
    ("2-", "Ruwbouw, omhulling"),
    ("21", "Buitenwanden"),
    ("21.1", "Metselwerk buitenspouwblad"),
    ("21.2", "Metselwerk binnenspouwblad"),
    ("21.3", "Spouwisolatie"),
    ("21.4", "Lateien"),
    ("21.5", "Raveelconstructies"),
    ("22", "Binnenwanden"),
    ("22.1", "Binnenwand kalkzandsteen"),
    ("22.2", "Binnenwand metalstud"),
    ("22.3", "Scheidingswand gipsblokken"),
    ("23", "Vloeren"),
    ("23.1", "Begane grondvloer"),
    ("23.2", "Vloerisolatie"),
    ("24", "Trappen en hellingen"),
    ("27", "Daken"),
    ("27.1", "Dakisolatie"),
    ("27.2", "Dakbedekking"),
    ("27.3", "Nokvorst en hulpstukken"),
    ("27.4", "Dakgoten"),
    ("27.5", "Hemelwaterafvoer"),
    ("28", "Hoofddraagconstructie"),
    # 3- Afbouw
    ("3-", "Afbouw"),
    ("31", "Buitenwandopeningen"),
    ("31.1", "Kozijnen kunststof"),
    ("31.2", "Openslaande deuren"),
    ("31.3", "Beglazing HR++"),
    ("31.4", "Voordeurkozijn"),
    ("31.5", "Achterdeurkozijn"),
    ("32", "Binnenwandopeningen"),
    ("32.1", "Binnendeuren opdek"),
    ("32.2", "Binnendeuren paneeldeur"),
    ("32.3", "Binnenkozijnen"),
    ("33", "Vloeropeningen"),
    ("34", "Balustrades en leuningen"),
    ("34.1", "Balustrade hout"),
    ("34.2", "Balustrade staal"),
    ("35", "Plafonds en wanden"),
    ("37", "Dakopeningen"),
    # 4- Afwerkingen
    ("4-", "Afwerkingen"),
    ("41", "Buitenwandafwerkingen"),
    ("41.1", "Voegwerk"),
    ("41.2", "Kozijnafwerking"),
    ("42", "Binnenwandafwerkingen"),
    ("42.1", "Stucwerk wanden"),
    ("42.2", "Tegelwerk wanden"),
    ("42.3", "Schilderwerk wanden"),
    ("43", "Vloerafwerkingen"),
    ("43.1", "Dekvloer"),
    ("43.2", "Vloertegels"),
    ("43.3", "Laminaatvloer"),
    ("44", "Trapafwerkingen"),
    ("45", "Plafondafwerkingen"),
    ("45.1", "Stucwerk plafonds"),
    ("45.2", "Schilderwerk plafonds"),
    ("47", "Dakafwerkingen"),
    ("48", "Beschermingen"),
    # 5- Installaties algemeen
    ("5-", "Installaties, algemeen"),
    ("52", "Afvoeren"),
    ("52.1", "Binnenriolering"),
    ("52.2", "Ontstoppingsstukken"),
    ("52.3", "Buitenriolering"),
    ("53", "Waterinstallaties"),
    ("53.1", "Waterleidingen koud"),
    ("53.2", "Waterleidingen warm"),
    ("53.3", "Watermeter"),
    ("54", "Gasinstallaties"),
    ("54.1", "Gasleidingen"),
    ("54.2", "Gasmeter"),
    ("55", "Koeling en verwarming"),
    ("55.1", "CV-ketel"),
    ("55.2", "CV-leidingen"),
    ("55.3", "Radiatoren"),
    ("55.4", "Radiatorkranen"),
    ("55.5", "Vloerverwarming"),
    ("56", "Luchtbehandeling"),
    ("56.1", "Mechanische ventilatie"),
    ("56.2", "Luchtkanalen"),
    ("56.3", "Ventilatieroosters"),
    ("57", "Elektra"),
    ("57.1", "Groepenkast"),
    ("57.2", "Bekabeling"),
    ("57.3", "Wandcontactdozen"),
    ("57.4", "Schakelaars"),
    ("57.5", "Lichtpunten"),
    ("57.6", "Buitenverlichting"),
    ("58", "Communicatie"),
    ("59", "Transport"),
    # 6- Installaties specifiek
    ("6-", "Installaties, specifiek"),
    ("61", "Centrale voorzieningen"),
    ("62", "Zonne-energie"),
    ("63", "Warmtepompen"),
    ("64", "Beveiliging"),
    ("65", "Brandbeveiliging"),
    ("66", "Bliksembeveiliging"),
    # 7- Vaste voorzieningen
    ("7-", "Vaste voorzieningen"),
    ("71", "Sanitair"),
    ("71.1", "Toiletcombinatie"),
    ("71.2", "Wastafel"),
    ("71.3", "Badkuip"),
    ("71.4", "Douchecabine"),
    ("71.5", "Badkamerkranen"),
    ("71.6", "Badkameraccessoires"),
    ("72", "Keukeninrichting"),
    ("72.1", "Keukenblok"),
    ("72.2", "Keukenapparatuur"),
    ("72.3", "Aanrechtblad"),
    ("73", "Vaste kasten"),
    ("74", "Werkbladen"),
    # 8- Losse inventaris
    ("8-", "Losse inventaris"),
    ("81", "Meubilair"),
    ("82", "Apparatuur"),
    ("83", "Kunst"),
    # 9- Terreinonderdelen
    ("9-", "Terreinonderdelen"),
    ("90", "Erfafscheidingen"),
    ("90.1", "Schutting"),
    ("91", "Tuinhuizen en bijgebouwen"),
    ("92", "Zwembaden"),
    ("93", "Beplanting"),
]


class StabuSearchDialog(QDialog):
    """Dialoog voor het zoeken en selecteren van STABU codes"""

    def __init__(self, parent=None, current_code: str = ""):
        super().__init__(parent)
        self.setWindowTitle("STABU-code zoeken")
        self.setMinimumSize(400, 500)
        self._selected_code = current_code

        self._setup_ui()
        self._load_codes()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Zoekbalk
        search_layout = QHBoxLayout()
        search_label = QLabel("Zoeken:")
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Typ om te zoeken...")
        self._search_input.textChanged.connect(self._filter_codes)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self._search_input)
        layout.addLayout(search_layout)

        # Lijst met codes
        self._code_list = QListWidget()
        self._code_list.itemDoubleClicked.connect(self._select_and_close)
        layout.addWidget(self._code_list)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _load_codes(self):
        """Laad alle STABU codes in de lijst"""
        self._code_list.clear()
        for code, description in STABU_CODES:
            item = QListWidgetItem(f"{code} - {description}")
            item.setData(Qt.UserRole, code)
            self._code_list.addItem(item)

            # Selecteer huidige code
            if code == self._selected_code:
                item.setSelected(True)
                self._code_list.setCurrentItem(item)

    def _filter_codes(self, text: str):
        """Filter de codes op basis van zoektekst"""
        text = text.lower()
        for i in range(self._code_list.count()):
            item = self._code_list.item(i)
            item_text = item.text().lower()
            item.setHidden(text not in item_text)

    def _select_and_close(self, item: QListWidgetItem):
        """Selecteer item en sluit dialoog"""
        self._selected_code = item.data(Qt.UserRole)
        self.accept()

    def _on_accept(self):
        """Verwerk OK button"""
        current = self._code_list.currentItem()
        if current:
            self._selected_code = current.data(Qt.UserRole)
        self.accept()

    def selected_code(self) -> str:
        """Geef de geselecteerde code terug"""
        return self._selected_code


class StabuEditorWidget(QWidget):
    """Custom editor widget voor STABU-code met zoekknop"""

    codeSelected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Tekstveld voor code
        self._line_edit = QLineEdit()
        self._line_edit.setFrame(False)
        layout.addWidget(self._line_edit, 1)

        # Zoekknop
        self._search_btn = QToolButton()
        self._search_btn.setText("...")
        self._search_btn.setFixedSize(20, 18)
        self._search_btn.setToolTip("STABU-code zoeken")
        self._search_btn.setStyleSheet("""
            QToolButton {
                border: 1px solid palette(mid);
                font-weight: bold;
            }
            QToolButton:hover {
                background: palette(highlight);
                color: palette(highlighted-text);
            }
        """)
        self._search_btn.clicked.connect(self._open_search)
        layout.addWidget(self._search_btn)

    def _open_search(self):
        """Open zoekdialoog"""
        dialog = StabuSearchDialog(self, self._line_edit.text())
        if dialog.exec() == QDialog.Accepted:
            self._line_edit.setText(dialog.selected_code())
            self.codeSelected.emit(dialog.selected_code())

    def text(self) -> str:
        return self._line_edit.text()

    def setText(self, text: str):
        self._line_edit.setText(text)

    def lineEdit(self) -> QLineEdit:
        return self._line_edit


class StabuDelegate(QStyledItemDelegate):
    """Delegate voor STABU-code invoer met zoekknop"""

    def createEditor(self, parent, option, index):
        editor = StabuEditorWidget(parent)
        return editor

    def setEditorData(self, editor, index):
        value = index.data(Qt.DisplayRole) or ""
        editor.setText(value)

    def setModelData(self, editor, model, index):
        value = editor.text()
        model.setData(index, value, Qt.DisplayRole)

        # Update ook het CostItem
        cost_item = model.get_item(index)
        if cost_item:
            cost_item.identification = value

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class SfbSearchDialog(QDialog):
    """Dialoog voor het zoeken en selecteren van SFB codes"""

    def __init__(self, parent=None, current_code: str = ""):
        super().__init__(parent)
        self.setWindowTitle("SFB-code zoeken")
        self.setMinimumSize(400, 500)
        self._selected_code = current_code

        self._setup_ui()
        self._load_codes()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Zoekbalk
        search_layout = QHBoxLayout()
        search_label = QLabel("Zoeken:")
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Typ om te zoeken...")
        self._search_input.textChanged.connect(self._filter_codes)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self._search_input)
        layout.addLayout(search_layout)

        # Lijst met codes
        self._code_list = QListWidget()
        self._code_list.itemDoubleClicked.connect(self._select_and_close)
        layout.addWidget(self._code_list)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _load_codes(self):
        """Laad alle SFB codes in de lijst"""
        self._code_list.clear()
        for code, description in SFB_CODES:
            item = QListWidgetItem(f"{code} - {description}")
            item.setData(Qt.UserRole, code)
            self._code_list.addItem(item)

            # Selecteer huidige code
            if code == self._selected_code:
                item.setSelected(True)
                self._code_list.setCurrentItem(item)

    def _filter_codes(self, text: str):
        """Filter de codes op basis van zoektekst"""
        text = text.lower()
        for i in range(self._code_list.count()):
            item = self._code_list.item(i)
            item_text = item.text().lower()
            item.setHidden(text not in item_text)

    def _select_and_close(self, item: QListWidgetItem):
        """Selecteer item en sluit dialoog"""
        self._selected_code = item.data(Qt.UserRole)
        self.accept()

    def _on_accept(self):
        """Verwerk OK button"""
        current = self._code_list.currentItem()
        if current:
            self._selected_code = current.data(Qt.UserRole)
        self.accept()

    def selected_code(self) -> str:
        """Geef de geselecteerde code terug"""
        return self._selected_code


class SfbEditorWidget(QWidget):
    """Custom editor widget voor SFB-code met zoekknop"""

    codeSelected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Tekstveld voor code
        self._line_edit = QLineEdit()
        self._line_edit.setFrame(False)
        layout.addWidget(self._line_edit, 1)

        # Zoekknop
        self._search_btn = QToolButton()
        self._search_btn.setText("...")
        self._search_btn.setFixedSize(20, 18)
        self._search_btn.setToolTip("SFB-code zoeken")
        self._search_btn.setStyleSheet("""
            QToolButton {
                border: 1px solid palette(mid);
                font-weight: bold;
            }
            QToolButton:hover {
                background: palette(highlight);
                color: palette(highlighted-text);
            }
        """)
        self._search_btn.clicked.connect(self._open_search)
        layout.addWidget(self._search_btn)

    def _open_search(self):
        """Open zoekdialoog"""
        dialog = SfbSearchDialog(self, self._line_edit.text())
        if dialog.exec() == QDialog.Accepted:
            self._line_edit.setText(dialog.selected_code())
            self.codeSelected.emit(dialog.selected_code())

    def text(self) -> str:
        return self._line_edit.text()

    def setText(self, text: str):
        self._line_edit.setText(text)

    def lineEdit(self) -> QLineEdit:
        return self._line_edit


class SfbDelegate(QStyledItemDelegate):
    """Delegate voor SFB-code invoer met zoekknop"""

    def createEditor(self, parent, option, index):
        editor = SfbEditorWidget(parent)
        return editor

    def setEditorData(self, editor, index):
        value = index.data(Qt.DisplayRole) or ""
        editor.setText(value)

    def setModelData(self, editor, model, index):
        value = editor.text()
        model.setData(index, value, Qt.DisplayRole)

        # Update ook het CostItem
        cost_item = model.get_item(index)
        if cost_item:
            cost_item.sfb_code = value

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class CostTreeModel(QStandardItemModel):
    """Model voor de kostenposten met hiërarchie (inklapbaar)"""

    COLUMNS = [
        ("Nr", "row_number"),
        ("STABU-code", "identification"),
        ("SFB-code", "sfb_code"),
        ("Omschrijving", "name"),
        ("Eenheid", "unit_symbol"),
        ("Hoeveelheid", "quantity"),
        ("Eenheidsprijs", "unit_price"),
        ("Totaal", "subtotal"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._schedule: Optional[CostSchedule] = None
        self._locale = QLocale(QLocale.Dutch, QLocale.Netherlands)
        self._row_counter = 0
        self._is_first_chapter = True
        self.setHorizontalHeaderLabels([col[0] for col in self.COLUMNS])

    def set_schedule(self, schedule: Optional[CostSchedule]):
        """Stel de begroting in"""
        self.clear()
        self.setHorizontalHeaderLabels([col[0] for col in self.COLUMNS])
        self._schedule = schedule
        self._row_counter = 0
        self._is_first_chapter = True

        if schedule:
            for item in schedule.items:
                self._add_item_to_model(item, self.invisibleRootItem(), is_root=True)

    def _create_separator_row(self):
        """Maak een grijze scheidingsregel"""
        separator_items = []
        for _ in self.COLUMNS:
            sep_item = QStandardItem("")
            sep_item.setEditable(False)
            sep_item.setEnabled(False)
            sep_item.setSelectable(False)
            sep_item.setBackground(QBrush(QColor(200, 200, 205)))
            sep_item.setFlags(Qt.NoItemFlags)
            separator_items.append(sep_item)
        return separator_items

    def _add_item_to_model(self, cost_item: CostItem, parent_item: QStandardItem, is_root: bool = False):
        """Voeg een CostItem toe aan het model"""

        # Voeg scheidingsregel toe voor hoofdstukken (behalve de eerste)
        if is_root and cost_item.is_chapter:
            if not self._is_first_chapter:
                parent_item.appendRow(self._create_separator_row())
            self._is_first_chapter = False

        self._row_counter += 1
        row_items = []

        # Nr kolom (eerste kolom voor tree hiërarchie)
        nr_item = QStandardItem(str(self._row_counter))
        nr_item.setData(cost_item, COST_ITEM_ROLE)
        nr_item.setEditable(False)
        nr_item.setTextAlignment(Qt.AlignCenter)
        row_items.append(nr_item)

        # STABU-code kolom
        code_item = QStandardItem(cost_item.identification or "")
        code_item.setData(cost_item, COST_ITEM_ROLE)
        code_item.setEditable(True)
        row_items.append(code_item)

        # SFB kolom - auto-populate als leeg op basis van STABU-code
        sfb_code = cost_item.sfb_code
        if not sfb_code and cost_item.identification:
            sfb_code = get_sfb_for_stabu(cost_item.identification)
            cost_item.sfb_code = sfb_code  # Sla op in het model

        sfb_item = QStandardItem(sfb_code or "")
        sfb_item.setData(cost_item, COST_ITEM_ROLE)
        sfb_item.setEditable(True)
        row_items.append(sfb_item)

        # Omschrijving kolom
        name_item = QStandardItem(cost_item.name or "")
        name_item.setData(cost_item, COST_ITEM_ROLE)
        name_item.setEditable(True)
        row_items.append(name_item)

        # Eenheid kolom - leeg voor tekstregels
        show_cost_data = cost_item.is_leaf and not cost_item.is_text_only
        unit_item = QStandardItem(cost_item.unit_symbol if show_cost_data else "")
        unit_item.setData(cost_item, COST_ITEM_ROLE)
        unit_item.setEditable(False)
        row_items.append(unit_item)

        # Hoeveelheid kolom - leeg voor tekstregels
        qty_text = self._locale.toString(cost_item.quantity, 'f', 2) if show_cost_data else ""
        qty_item = QStandardItem(qty_text)
        qty_item.setData(cost_item, COST_ITEM_ROLE)
        qty_item.setData(cost_item.quantity if show_cost_data else None, Qt.EditRole)
        qty_item.setEditable(show_cost_data)
        qty_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        row_items.append(qty_item)

        # Eenheidsprijs kolom (met euro teken) - leeg voor tekstregels
        price_text = f"€ {self._locale.toString(cost_item.unit_price, 'f', 2)}" if show_cost_data else ""
        price_item = QStandardItem(price_text)
        price_item.setData(cost_item, COST_ITEM_ROLE)
        price_item.setData(cost_item.unit_price if show_cost_data else None, Qt.EditRole)
        price_item.setEditable(show_cost_data)
        price_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        row_items.append(price_item)

        # Totaal kolom (met euro teken) - leeg voor tekstregels
        if cost_item.is_text_only:
            total_text = ""
        else:
            total_text = f"€ {self._locale.toString(cost_item.subtotal, 'f', 2)}"
        total_item = QStandardItem(total_text)
        total_item.setData(cost_item, COST_ITEM_ROLE)
        total_item.setEditable(False)
        total_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        row_items.append(total_item)

        # Stijl voor hoofdstukken (bold + lichte achtergrond)
        if cost_item.is_chapter:
            font = QFont()
            font.setBold(True)
            bg_color = QColor(240, 240, 245)
            for item in row_items:
                item.setFont(font)
                item.setBackground(QBrush(bg_color))

        # Stijl voor tekstregels (italic + grijze tekst)
        if cost_item.is_text_only:
            font = QFont()
            font.setItalic(True)
            text_color = QColor(100, 100, 100)  # Grijs
            for item in row_items:
                item.setFont(font)
                item.setForeground(QBrush(text_color))

        # Tooltip met details
        tooltip = f"{cost_item.identification} - {cost_item.name}"
        if cost_item.sfb_code:
            tooltip += f"\nSFB: {cost_item.sfb_code}"
        if cost_item.description:
            tooltip += f"\n{cost_item.description}"
        for item in row_items:
            item.setToolTip(tooltip)

        parent_item.appendRow(row_items)

        # Recursief children toevoegen aan eerste kolom item (Nr voor tree hiërarchie)
        for child in cost_item.children:
            self._add_item_to_model(child, nr_item, is_root=False)

    def refresh(self):
        """Vernieuw het model"""
        schedule = self._schedule
        self.set_schedule(schedule)

    def get_item(self, index: QModelIndex) -> Optional[CostItem]:
        """Haal het CostItem op voor een index"""
        if not index.isValid():
            return None
        # Eerste kolom gebruiken voor data
        first_col_index = self.index(index.row(), 0, index.parent())
        item = self.itemFromIndex(first_col_index)
        if item:
            return item.data(COST_ITEM_ROLE)
        return None

    def get_item_row(self, item: CostItem) -> QModelIndex:
        """Haal de index op voor een item"""
        return self._find_item_index(item)

    def _find_item_index(self, cost_item: CostItem, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        """Zoek de index voor een item"""
        for row in range(self.rowCount(parent)):
            index = self.index(row, 0, parent)
            item = self.itemFromIndex(index)
            if item and item.data(COST_ITEM_ROLE) == cost_item:
                return index
            # Zoek recursief in children
            child_index = self._find_item_index(cost_item, index)
            if child_index.isValid():
                return child_index
        return QModelIndex()

    def update_parent_totals(self, index: QModelIndex):
        """Update de totalen van alle parent items"""
        locale = QLocale(QLocale.Dutch, QLocale.Netherlands)

        # Loop door alle parents
        parent_index = index.parent()
        while parent_index.isValid():
            parent_item = self.get_item(parent_index)
            if parent_item:
                # Update totaal kolom (kolom 7)
                total_index = self.index(parent_index.row(), 7, parent_index.parent())
                total_text = f"€ {locale.toString(parent_item.subtotal, 'f', 2)}"
                self.setData(total_index, total_text, Qt.DisplayRole)
            parent_index = parent_index.parent()


class NumericDelegate(QStyledItemDelegate):
    """Delegate voor numerieke invoer met euro teken"""

    def createEditor(self, parent, option, index):
        editor = QDoubleSpinBox(parent)
        editor.setMinimum(0)
        editor.setMaximum(999999999)
        editor.setDecimals(2)
        editor.setSingleStep(1.0)
        editor.setPrefix("€ ")
        return editor

    def setEditorData(self, editor, index):
        value = index.data(Qt.EditRole)
        if value is not None:
            try:
                editor.setValue(float(value))
            except (TypeError, ValueError):
                editor.setValue(0)

    def setModelData(self, editor, model, index):
        value = editor.value()
        model.setData(index, value, Qt.EditRole)

        # Update ook het CostItem
        cost_item = model.get_item(index)
        if cost_item:
            col = index.column()
            if col == 5:  # Hoeveelheid
                cost_item.quantity = value
            elif col == 6:  # Eenheidsprijs
                cost_item.unit_price = value

            # Update Totaal kolom (kolom 7)
            total_index = model.index(index.row(), 7, index.parent())
            locale = QLocale(QLocale.Dutch, QLocale.Netherlands)
            total_text = f"€ {locale.toString(cost_item.subtotal, 'f', 2)}"
            model.setData(total_index, total_text, Qt.DisplayRole)

            # Update parent totalen
            model.update_parent_totals(index)


class QuantityEditorWidget(QWidget):
    """Custom editor widget met spinbox en calculator knop"""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Spinbox voor waarde
        self._spinbox = QDoubleSpinBox()
        self._spinbox.setMinimum(0)
        self._spinbox.setMaximum(999999999)
        self._spinbox.setDecimals(2)
        self._spinbox.setSingleStep(1.0)
        self._spinbox.setFrame(False)
        layout.addWidget(self._spinbox, 1)

        # Calculator knop
        self._calc_btn = QToolButton()
        self._calc_btn.setIcon(IconProvider.get_icon("calculator", 16))
        self._calc_btn.setIconSize(QSize(14, 14))
        self._calc_btn.setFixedSize(18, 18)
        self._calc_btn.setToolTip("Calculator")
        self._calc_btn.setStyleSheet("""
            QToolButton {
                border: none;
                background: transparent;
                padding: 1px;
            }
            QToolButton:hover {
                background: palette(highlight);
                border-radius: 2px;
            }
        """)
        layout.addWidget(self._calc_btn)

    def value(self) -> float:
        return self._spinbox.value()

    def setValue(self, value: float):
        self._spinbox.setValue(value)

    def spinbox(self) -> QDoubleSpinBox:
        return self._spinbox


class QuantityDelegate(QStyledItemDelegate):
    """Delegate voor hoeveelheid invoer met calculator icoon"""

    def createEditor(self, parent, option, index):
        editor = QuantityEditorWidget(parent)
        return editor

    def setEditorData(self, editor, index):
        value = index.data(Qt.EditRole)
        if value is not None:
            try:
                editor.setValue(float(value))
            except (TypeError, ValueError):
                editor.setValue(0)

    def setModelData(self, editor, model, index):
        value = editor.value()
        model.setData(index, value, Qt.EditRole)

        cost_item = model.get_item(index)
        if cost_item:
            cost_item.quantity = value

            # Update Totaal kolom (kolom 7)
            total_index = model.index(index.row(), 7, index.parent())
            locale = QLocale(QLocale.Dutch, QLocale.Netherlands)
            total_text = f"€ {locale.toString(cost_item.subtotal, 'f', 2)}"
            model.setData(total_index, total_text, Qt.DisplayRole)

            # Update parent totalen
            model.update_parent_totals(index)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class CostTableView(QWidget):
    """Widget voor de tabel weergave met inklapbare hoofdstukken

    Gebaseerd op WpCalc interface principes:
    - Native Qt TreeView voor snelle expand/collapse
    - STABU hoofdstukken met visuele scheiding
    - Intuïtieve Excel-achtige interface
    """

    itemSelected = Signal(object)  # CostItem of None
    itemChanged = Signal(object)   # CostItem

    def __init__(self, parent=None):
        super().__init__(parent)

        self._schedule: Optional[CostSchedule] = None
        self._model = CostTreeModel()

        # Zoom level (percentage)
        self._zoom_level = 100
        self._min_zoom = 50
        self._max_zoom = 200

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Stel de UI in"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Tree view met native expand/collapse
        self._tree = QTreeView()
        self._tree.setModel(self._model)
        self._tree.setAlternatingRowColors(True)
        self._tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self._tree.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._tree.setSortingEnabled(False)
        self._tree.setWordWrap(False)

        # Native expand/collapse instellingen
        self._tree.setAnimated(True)
        self._tree.setIndentation(20)
        self._tree.setRootIsDecorated(True)  # Toon +/- iconen
        self._tree.setItemsExpandable(True)
        self._tree.setExpandsOnDoubleClick(True)

        # Bepaal paden naar custom expand/collapse iconen
        assets_dir = Path(__file__).parent.parent.parent / "assets"
        expand_icon = str(assets_dir / "tree_expand.png").replace("\\", "/")
        collapse_icon = str(assets_dir / "tree_collapse.png").replace("\\", "/")

        # Styling met custom branch iconen en lichtere selectiekleur
        self._base_font_size = 9
        self._tree.setStyleSheet(f"""
            QTreeView {{
                font-size: {self._base_font_size}pt;
            }}
            QTreeView::item {{
                padding: 2px 4px;
                min-height: 18px;
            }}
            QTreeView::item:selected {{
                background-color: #b3d9ff;
                color: #1a1a1a;
            }}
            QTreeView::item:selected:active {{
                background-color: #99ccff;
                color: #000000;
            }}
            QTreeView::item:hover:!selected {{
                background-color: #e6f2ff;
            }}
            QTreeView::branch:has-children:!has-siblings:closed,
            QTreeView::branch:closed:has-children:has-siblings {{
                image: url({expand_icon});
            }}
            QTreeView::branch:open:has-children:!has-siblings,
            QTreeView::branch:open:has-children:has-siblings {{
                image: url({collapse_icon});
            }}
            QHeaderView::section {{
                padding: 6px 8px;
                font-weight: bold;
                font-size: 9pt;
            }}
        """)

        # Delegates voor kolommen
        stabu_delegate = StabuDelegate(self)
        sfb_delegate = SfbDelegate(self)
        qty_delegate = QuantityDelegate(self)
        price_delegate = NumericDelegate(self)
        self._tree.setItemDelegateForColumn(1, stabu_delegate)  # STABU-code
        self._tree.setItemDelegateForColumn(2, sfb_delegate)    # SFB-code
        self._tree.setItemDelegateForColumn(5, qty_delegate)    # Hoeveelheid
        self._tree.setItemDelegateForColumn(6, price_delegate)  # Eenheidsprijs

        # Header configuratie
        header = self._tree.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Nr (tree)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # STABU-code
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # SFB
        header.setSectionResizeMode(3, QHeaderView.Stretch)           # Omschrijving
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Eenheid
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Hoeveelheid
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Prijs
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Totaal
        header.setMinimumSectionSize(50)
        header.resizeSection(3, 300)  # Omschrijving standaard breder

        # Context menu
        self._tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._show_context_menu)

        layout.addWidget(self._tree)

        # Totalen balk onderaan
        self._setup_totals_bar(layout)

    def _setup_totals_bar(self, layout):
        """Setup de totalen balk onderaan"""
        self._totals_frame = QFrame()
        self._totals_frame.setFrameShape(QFrame.StyledPanel)
        self._totals_frame.setStyleSheet("""
            QFrame {
                border-top: 2px solid palette(mid);
                padding: 8px;
            }
            QLabel {
                font-weight: bold;
            }
        """)
        totals_layout = QHBoxLayout(self._totals_frame)
        totals_layout.setContentsMargins(10, 8, 10, 8)

        totals_layout.addStretch()

        self._subtotal_label = QLabel("Subtotaal: € 0,00")
        self._subtotal_label.setStyleSheet("font-size: 10pt;")
        totals_layout.addWidget(self._subtotal_label)

        totals_layout.addSpacing(30)

        self._btw_label = QLabel("BTW (21%): € 0,00")
        self._btw_label.setStyleSheet("font-size: 10pt;")
        totals_layout.addWidget(self._btw_label)

        totals_layout.addSpacing(30)

        self._total_label = QLabel("Totaal: € 0,00")
        self._total_label.setStyleSheet("color: #0ea5e9; font-size: 12pt; font-weight: bold;")
        totals_layout.addWidget(self._total_label)

        layout.addWidget(self._totals_frame)

    def _connect_signals(self):
        """Verbind signalen"""
        self._tree.selectionModel().currentRowChanged.connect(self._on_selection_changed)
        self._model.dataChanged.connect(self._on_data_changed)

        # Header click voor sorteren
        header = self._tree.header()
        header.setSectionsClickable(True)
        header.sectionClicked.connect(self._on_header_clicked)

        # Sorteer status bijhouden
        self._sort_column = -1
        self._sort_order = Qt.AscendingOrder

    def set_schedule(self, schedule: Optional[CostSchedule]):
        """Stel de begroting in"""
        self._schedule = schedule
        self._model.set_schedule(schedule)
        self._tree.expandAll()
        self._update_totals()

    def refresh(self):
        """Vernieuw de weergave"""
        self._model.refresh()
        self._tree.expandAll()
        self._update_totals()

    def _update_totals(self):
        """Update de totalen balk"""
        if self._schedule:
            locale = QLocale(QLocale.Dutch, QLocale.Netherlands)
            subtotal = self._schedule.subtotal
            btw_rate = getattr(self._schedule, 'vat_rate', 21)
            btw = subtotal * (btw_rate / 100)
            total = subtotal + btw

            self._subtotal_label.setText(f"Subtotaal: € {locale.toString(subtotal, 'f', 2)}")
            self._btw_label.setText(f"BTW ({btw_rate}%): € {locale.toString(btw, 'f', 2)}")
            self._total_label.setText(f"Totaal: € {locale.toString(total, 'f', 2)}")
        else:
            self._subtotal_label.setText("Subtotaal: € 0,00")
            self._btw_label.setText("BTW (21%): € 0,00")
            self._total_label.setText("Totaal: € 0,00")

    def get_selected_item(self) -> Optional[CostItem]:
        """Haal het geselecteerde item op"""
        index = self._tree.currentIndex()
        if index.isValid():
            return self._model.get_item(index)
        return None

    def get_selected_index(self) -> QModelIndex:
        """Haal de geselecteerde index op"""
        return self._tree.currentIndex()

    def select_item(self, item: CostItem):
        """Selecteer een specifiek item"""
        index = self._model.get_item_row(item)
        if index.isValid():
            self._tree.setCurrentIndex(index)
            self._tree.scrollTo(index)

    def _on_selection_changed(self, current: QModelIndex, previous: QModelIndex):
        """Afhandeling van selectie wijziging"""
        item = self._model.get_item(current) if current.isValid() else None
        self.itemSelected.emit(item)

    def _on_data_changed(self, topLeft: QModelIndex, bottomRight: QModelIndex, roles):
        """Afhandeling van data wijziging"""
        # Prevent re-entry
        if getattr(self, '_handling_data_change', False):
            return
        self._handling_data_change = True

        try:
            # Bewaar huidige positie
            current_index = self._tree.currentIndex()
            scroll_pos = self._tree.verticalScrollBar().value()

            item = self._model.get_item(topLeft)
            if item:
                self.itemChanged.emit(item)
                self._update_totals()

            # Herstel positie
            if current_index.isValid():
                self._tree.setCurrentIndex(current_index)
            self._tree.verticalScrollBar().setValue(scroll_pos)
        finally:
            self._handling_data_change = False

    def _on_header_clicked(self, logical_index: int):
        """Afhandeling van header kolom klik voor sortering"""
        # Toggle sorteer volgorde als dezelfde kolom wordt geklikt
        if self._sort_column == logical_index:
            if self._sort_order == Qt.AscendingOrder:
                self._sort_order = Qt.DescendingOrder
            else:
                # Reset sortering na descending
                self._sort_column = -1
                self._sort_order = Qt.AscendingOrder
                self._reset_sort()
                return
        else:
            self._sort_column = logical_index
            self._sort_order = Qt.AscendingOrder

        # Sorteer de begroting
        self._sort_schedule(logical_index, self._sort_order)

    def _sort_schedule(self, column: int, order: Qt.SortOrder):
        """Sorteer de begroting op basis van kolom"""
        if not self._schedule:
            return

        # Bewaar scroll positie
        scroll_pos = self._tree.verticalScrollBar().value()

        # Bepaal sorteer attribuut
        column_attrs = {
            1: "identification",  # STABU-code
            2: "sfb_code",        # SFB-code
            3: "name",            # Omschrijving
            7: "subtotal",        # Totaal
        }

        if column not in column_attrs:
            return

        attr = column_attrs[column]
        reverse = (order == Qt.DescendingOrder)

        def sort_key(item):
            val = getattr(item, attr, "") or ""
            # Numerieke waarden sorteren als float
            if attr in ("subtotal", "quantity", "unit_price"):
                return val if isinstance(val, (int, float)) else 0
            return str(val).lower()

        # Sorteer elk hoofdstuk intern
        for chapter in self._schedule.items:
            if chapter.children:
                chapter.children.sort(key=sort_key, reverse=reverse)
                # Recursief sorteren van sub-items
                self._sort_children_recursive(chapter, sort_key, reverse)

        # Refresh de view
        self._model.set_schedule(self._schedule)
        self._tree.expandAll()

        # Herstel scroll positie
        self._tree.verticalScrollBar().setValue(scroll_pos)

    def _sort_children_recursive(self, parent_item: CostItem, sort_key, reverse: bool):
        """Sorteer children recursief"""
        for child in parent_item.children:
            if child.children:
                child.children.sort(key=sort_key, reverse=reverse)
                self._sort_children_recursive(child, sort_key, reverse)

    def _reset_sort(self):
        """Reset de sortering naar originele volgorde (STABU-code)"""
        if not self._schedule:
            return

        # Bewaar scroll positie
        scroll_pos = self._tree.verticalScrollBar().value()

        def stabu_sort_key(item):
            return item.identification or ""

        # Sorteer terug op STABU-code
        for chapter in self._schedule.items:
            if chapter.children:
                chapter.children.sort(key=stabu_sort_key)
                self._sort_children_recursive(chapter, stabu_sort_key, False)

        # Refresh de view
        self._model.set_schedule(self._schedule)
        self._tree.expandAll()

        # Herstel scroll positie
        self._tree.verticalScrollBar().setValue(scroll_pos)

    def _show_context_menu(self, position):
        """Toon context menu"""
        index = self._tree.indexAt(position)
        item = self._model.get_item(index) if index.isValid() else None

        menu = QMenu(self)

        # Toevoegen acties
        add_chapter_action = QAction("Hoofdstuk toevoegen", self)
        add_chapter_action.triggered.connect(lambda: self._add_chapter(item))
        menu.addAction(add_chapter_action)

        add_action = QAction("Kostenpost toevoegen", self)
        add_action.triggered.connect(lambda: self._add_cost_item(item))
        menu.addAction(add_action)

        if item:
            menu.addSeparator()

            # Expand/Collapse voor items met children
            if item.children:
                if self._tree.isExpanded(index):
                    collapse_action = QAction("Inklappen", self)
                    collapse_action.triggered.connect(lambda: self._tree.collapse(index))
                    menu.addAction(collapse_action)
                else:
                    expand_action = QAction("Uitklappen", self)
                    expand_action.triggered.connect(lambda: self._tree.expand(index))
                    menu.addAction(expand_action)

                menu.addSeparator()

            # Bewerk acties
            edit_action = QAction("Bewerken", self)
            edit_action.triggered.connect(lambda: self._tree.edit(index))
            menu.addAction(edit_action)

            delete_action = QAction("Verwijderen", self)
            delete_action.triggered.connect(lambda: self._delete_item(item))
            menu.addAction(delete_action)

            # Eenheid wijzigen submenu
            if item.is_leaf:
                menu.addSeparator()
                unit_menu = menu.addMenu("Eenheid wijzigen")
                for qt in QuantityType:
                    action = QAction(f"{qt.unit_symbol} ({qt.unit_name})", self)
                    action.triggered.connect(
                        lambda checked, q=qt: self._change_unit(item, q)
                    )
                    unit_menu.addAction(action)

        menu.exec_(self._tree.viewport().mapToGlobal(position))

    def _delete_item(self, item: CostItem):
        """Verwijder een item"""
        # Bewaar scroll positie
        scroll_pos = self._tree.verticalScrollBar().value()

        if item.parent:
            item.parent.remove_child(item)
        elif self._schedule:
            self._schedule.remove_item(item)
        self.refresh()
        self.itemChanged.emit(item)

        # Herstel scroll positie
        self._tree.verticalScrollBar().setValue(scroll_pos)

    def _add_chapter(self, selected_item: Optional[CostItem] = None):
        """Voeg een nieuw hoofdstuk toe na het geselecteerde item"""
        if not self._schedule:
            return

        new_chapter = CostItem(
            name="Nieuw hoofdstuk",
            identification="XX",
        )

        if selected_item:
            # Zoek het root hoofdstuk waar dit item bij hoort
            root_item = selected_item
            while root_item.parent:
                root_item = root_item.parent

            # Voeg het nieuwe hoofdstuk toe na dit root item
            try:
                index = self._schedule.items.index(root_item)
                self._schedule.items.insert(index + 1, new_chapter)
                new_chapter.schedule = self._schedule
            except ValueError:
                self._schedule.add_item(new_chapter)
        else:
            self._schedule.add_item(new_chapter)

        self.refresh()
        self.itemChanged.emit(new_chapter)

        # Selecteer het nieuwe hoofdstuk
        self.select_item(new_chapter)

    def _add_cost_item(self, selected_item: Optional[CostItem] = None):
        """Voeg een nieuwe kostenpost toe binnen het geselecteerde hoofdstuk"""
        if not self._schedule:
            return

        new_item = CostItem(
            name="Nieuwe kostenpost",
            identification="",
        )

        if selected_item:
            # Zoek het hoofdstuk waar dit item bij hoort
            parent_chapter = selected_item
            while parent_chapter.parent:
                parent_chapter = parent_chapter.parent

            # Voeg toe aan dit hoofdstuk
            if selected_item == parent_chapter:
                # Geselecteerde item is zelf een hoofdstuk, voeg als eerste child toe
                parent_chapter.children.insert(0, new_item)
                new_item.parent = parent_chapter
                new_item.schedule = self._schedule
            else:
                # Voeg toe na het geselecteerde item binnen hetzelfde parent
                parent = selected_item.parent if selected_item.parent else parent_chapter
                try:
                    index = parent.children.index(selected_item)
                    parent.children.insert(index + 1, new_item)
                    new_item.parent = parent
                    new_item.schedule = self._schedule
                except ValueError:
                    parent.add_child(new_item)
        else:
            # Geen selectie, voeg toe aan eerste hoofdstuk of maak nieuw
            if self._schedule.items:
                self._schedule.items[0].add_child(new_item)
            else:
                # Maak eerst een hoofdstuk
                chapter = CostItem(name="Hoofdstuk 1", identification="01")
                self._schedule.add_item(chapter)
                chapter.add_child(new_item)

        self.refresh()
        self.itemChanged.emit(new_item)

        # Selecteer het nieuwe item
        self.select_item(new_item)

    def _change_unit(self, item: CostItem, quantity_type: QuantityType):
        """Wijzig de eenheid van een item"""
        item.quantity_type = quantity_type
        self.refresh()
        self.itemChanged.emit(item)

    def collapse_all(self):
        """Klap alle hoofdstukken in"""
        self._tree.collapseAll()

    def expand_all(self):
        """Klap alle hoofdstukken uit"""
        self._tree.expandAll()

    def wheelEvent(self, event):
        """Handle wheel events voor Ctrl+Scroll zoom"""
        if event.modifiers() == Qt.ControlModifier:
            # Zoom in/out
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            elif delta < 0:
                self.zoom_out()
            event.accept()
        else:
            # Normale scroll
            super().wheelEvent(event)

    def zoom_in(self):
        """Zoom in (vergroot lettergrootte)"""
        if self._zoom_level < self._max_zoom:
            self._zoom_level += 10
            self._apply_zoom()

    def zoom_out(self):
        """Zoom uit (verklein lettergrootte)"""
        if self._zoom_level > self._min_zoom:
            self._zoom_level -= 10
            self._apply_zoom()

    def zoom_reset(self):
        """Reset zoom naar 100%"""
        self._zoom_level = 100
        self._apply_zoom()

    def _apply_zoom(self):
        """Pas zoom toe op de tree view"""
        # Bereken nieuwe lettergrootte
        new_font_size = self._base_font_size * self._zoom_level / 100

        # Bepaal paden naar custom expand/collapse iconen
        assets_dir = Path(__file__).parent.parent.parent / "assets"
        expand_icon = str(assets_dir / "tree_expand.png").replace("\\", "/")
        collapse_icon = str(assets_dir / "tree_collapse.png").replace("\\", "/")

        # Update stylesheet met nieuwe lettergrootte
        self._tree.setStyleSheet(f"""
            QTreeView {{
                font-size: {new_font_size}pt;
            }}
            QTreeView::item {{
                padding: 2px 4px;
                min-height: {int(18 * self._zoom_level / 100)}px;
            }}
            QTreeView::item:selected {{
                background-color: #b3d9ff;
                color: #1a1a1a;
            }}
            QTreeView::item:selected:active {{
                background-color: #99ccff;
                color: #000000;
            }}
            QTreeView::item:hover:!selected {{
                background-color: #e6f2ff;
            }}
            QTreeView::branch:has-children:!has-siblings:closed,
            QTreeView::branch:closed:has-children:has-siblings {{
                image: url({expand_icon});
            }}
            QTreeView::branch:open:has-children:!has-siblings,
            QTreeView::branch:open:has-children:has-siblings {{
                image: url({collapse_icon});
            }}
            QHeaderView::section {{
                padding: 6px 8px;
                font-weight: bold;
                font-size: {new_font_size}pt;
            }}
        """)

        # Update statusbar met zoom level (als parent beschikbaar is)
        parent = self.parent()
        while parent:
            if hasattr(parent, '_statusbar'):
                parent._statusbar.showMessage(f"Zoom: {self._zoom_level}%", 2000)
                break
            parent = parent.parent() if hasattr(parent, 'parent') else None

    def get_zoom_level(self) -> int:
        """Haal huidige zoom level op"""
        return self._zoom_level

    def set_zoom_level(self, level: int):
        """Stel zoom level in"""
        self._zoom_level = max(self._min_zoom, min(self._max_zoom, level))
        self._apply_zoom()

    def toggle_item(self, item: CostItem):
        """Toggle in/uitklappen van een item"""
        index = self._model.get_item_row(item)
        if index.isValid():
            if self._tree.isExpanded(index):
                self._tree.collapse(index)
            else:
                self._tree.expand(index)
