"""
PropertiesPanel - Eigenschappen paneel voor geselecteerde items
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QTextEdit, QDoubleSpinBox,
    QComboBox, QGroupBox, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from pathlib import Path

from typing import Optional
from ..models import CostItem
from ..models.cost_value import QuantityType


class PropertiesPanel(QWidget):
    """Eigenschappen paneel voor het bewerken van kostenposten"""

    itemChanged = Signal(object)  # CostItem

    def __init__(self, parent=None):
        super().__init__(parent)

        self._item: Optional[CostItem] = None
        self._updating = False  # Voorkom recursieve updates

        self._setup_ui()
        self._connect_signals()
        self.clear()

    def _setup_ui(self):
        """Stel de UI in"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header met logo
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0ea5e9, stop:1 #06b6d4);
                border: none;
                border-bottom: 2px solid #0284c7;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 8, 12, 8)

        # Logo
        self._logo_label = QLabel()
        logo_path = Path(__file__).parent.parent.parent / "assets" / "logo_32.png"
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            self._logo_label.setPixmap(pixmap.scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self._logo_label.setText("🏗️")
            self._logo_label.setStyleSheet("font-size: 20px;")
        header_layout.addWidget(self._logo_label)

        # Titel
        title_label = QLabel("Eigenschappen")
        title_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: white;
            padding-left: 8px;
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        # Versie/branding
        brand_label = QLabel("OpenCalc")
        brand_label.setStyleSheet("""
            font-size: 10px;
            color: rgba(255, 255, 255, 0.7);
            font-style: italic;
        """)
        header_layout.addWidget(brand_label)

        main_layout.addWidget(header)

        # Content container
        content = QWidget()
        layout = QHBoxLayout(content)
        layout.setContentsMargins(10, 10, 10, 10)

        main_layout.addWidget(content, 1)

        # Linker kolom - Algemene eigenschappen
        left_group = QGroupBox("Algemeen")
        left_layout = QFormLayout(left_group)

        self._code_edit = QLineEdit()
        self._code_edit.setMaxLength(50)
        left_layout.addRow("Code:", self._code_edit)

        self._name_edit = QLineEdit()
        self._name_edit.setMaxLength(200)
        left_layout.addRow("Omschrijving:", self._name_edit)

        self._desc_edit = QTextEdit()
        self._desc_edit.setMaximumHeight(60)
        self._desc_edit.setPlaceholderText("Uitgebreide omschrijving...")
        left_layout.addRow("Details:", self._desc_edit)

        layout.addWidget(left_group, stretch=2)

        # Midden kolom - Kosten
        middle_group = QGroupBox("Kosten")
        middle_layout = QFormLayout(middle_group)

        # Eenheid
        self._unit_combo = QComboBox()
        for qt in QuantityType:
            self._unit_combo.addItem(f"{qt.unit_symbol} - {qt.unit_name}", qt)
        middle_layout.addRow("Eenheid:", self._unit_combo)

        # Hoeveelheid
        self._quantity_spin = QDoubleSpinBox()
        self._quantity_spin.setMinimum(0)
        self._quantity_spin.setMaximum(999999999)
        self._quantity_spin.setDecimals(3)
        self._quantity_spin.setSingleStep(1.0)
        middle_layout.addRow("Hoeveelheid:", self._quantity_spin)

        # Eenheidsprijs
        self._price_spin = QDoubleSpinBox()
        self._price_spin.setMinimum(0)
        self._price_spin.setMaximum(999999999)
        self._price_spin.setDecimals(2)
        self._price_spin.setSingleStep(1.0)
        self._price_spin.setPrefix("€ ")
        middle_layout.addRow("Eenheidsprijs:", self._price_spin)

        layout.addWidget(middle_group, stretch=1)

        # Rechter kolom - Totalen
        right_group = QGroupBox("Totalen")
        right_layout = QFormLayout(right_group)

        # Subtotaal
        self._subtotal_label = QLabel("€ 0,00")
        self._subtotal_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        right_layout.addRow("Subtotaal:", self._subtotal_label)

        # Niveau indicator
        self._level_label = QLabel("-")
        right_layout.addRow("Niveau:", self._level_label)

        # Type indicator
        self._type_label = QLabel("-")
        right_layout.addRow("Type:", self._type_label)

        layout.addWidget(right_group, stretch=1)

    def _connect_signals(self):
        """Verbind signalen"""
        self._code_edit.editingFinished.connect(self._on_code_changed)
        self._name_edit.editingFinished.connect(self._on_name_changed)
        self._desc_edit.textChanged.connect(self._on_desc_changed)
        self._unit_combo.currentIndexChanged.connect(self._on_unit_changed)
        self._quantity_spin.valueChanged.connect(self._on_quantity_changed)
        self._price_spin.valueChanged.connect(self._on_price_changed)

    def set_item(self, item: Optional[CostItem]):
        """Stel het te bewerken item in"""
        self._item = item
        self._update_ui()

    def clear(self):
        """Wis het paneel"""
        self._item = None
        self._update_ui()

    def _update_ui(self):
        """Update de UI met item data"""
        self._updating = True

        if self._item:
            self._code_edit.setText(self._item.identification)
            self._name_edit.setText(self._item.name)
            self._desc_edit.setPlainText(self._item.description)

            # Vind de juiste index voor quantity type
            for i in range(self._unit_combo.count()):
                if self._unit_combo.itemData(i) == self._item.quantity_type:
                    self._unit_combo.setCurrentIndex(i)
                    break

            self._quantity_spin.setValue(self._item.quantity)
            self._price_spin.setValue(self._item.unit_price)
            self._subtotal_label.setText(self._item.format_subtotal())
            self._level_label.setText(str(self._item.level))
            self._type_label.setText("Hoofdstuk" if self._item.is_chapter else "Kostenpost")

            # Enable/disable kosten velden
            is_leaf = self._item.is_leaf
            self._unit_combo.setEnabled(is_leaf)
            self._quantity_spin.setEnabled(is_leaf)
            self._price_spin.setEnabled(is_leaf)

            self.setEnabled(True)
        else:
            self._code_edit.clear()
            self._name_edit.clear()
            self._desc_edit.clear()
            self._unit_combo.setCurrentIndex(0)
            self._quantity_spin.setValue(0)
            self._price_spin.setValue(0)
            self._subtotal_label.setText("€ 0,00")
            self._level_label.setText("-")
            self._type_label.setText("-")

            self.setEnabled(False)

        self._updating = False

    def _emit_change(self):
        """Emit change signaal als niet in update modus"""
        if not self._updating and self._item:
            self._subtotal_label.setText(self._item.format_subtotal())
            self.itemChanged.emit(self._item)

    def _on_code_changed(self):
        """Afhandeling van code wijziging"""
        if self._item and not self._updating:
            self._item.identification = self._code_edit.text()
            self._emit_change()

    def _on_name_changed(self):
        """Afhandeling van naam wijziging"""
        if self._item and not self._updating:
            self._item.name = self._name_edit.text()
            self._emit_change()

    def _on_desc_changed(self):
        """Afhandeling van beschrijving wijziging"""
        if self._item and not self._updating:
            self._item.description = self._desc_edit.toPlainText()
            self._emit_change()

    def _on_unit_changed(self, index: int):
        """Afhandeling van eenheid wijziging"""
        if self._item and not self._updating:
            quantity_type = self._unit_combo.itemData(index)
            if quantity_type:
                self._item.quantity_type = quantity_type
                self._emit_change()

    def _on_quantity_changed(self, value: float):
        """Afhandeling van hoeveelheid wijziging"""
        if self._item and not self._updating:
            self._item.quantity = value
            self._emit_change()

    def _on_price_changed(self, value: float):
        """Afhandeling van prijs wijziging"""
        if self._item and not self._updating:
            self._item.unit_price = value
            self._emit_change()
