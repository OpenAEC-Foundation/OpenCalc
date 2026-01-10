"""
Surcharges Panel - Opslagen overzicht met berekeningen
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QFrame, QDoubleSpinBox, QGroupBox, QFormLayout,
    QAbstractItemView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

from typing import Optional
from ..models import CostSchedule


class SurchargesPanel(QWidget):
    """Panel voor opslagen en totaalberekening"""

    surchargesChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._schedule: Optional[CostSchedule] = None

        # Opslagen percentages
        self._algemene_kosten = 8.0  # AK %
        self._winst_risico = 3.0     # W&R %
        self._btw_percentage = 21.0  # BTW %

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Header
        header = QLabel("Opslagen en Totaalberekening")
        header.setStyleSheet("""
            font-size: 16pt;
            font-weight: bold;
            color: #1a237e;
            padding-bottom: 8px;
        """)
        layout.addWidget(header)

        # Hoofdstukken samenvatting
        chapters_group = QGroupBox("Hoofdstukken Samenvatting")
        chapters_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
        """)
        chapters_layout = QVBoxLayout(chapters_group)

        self._chapters_table = QTableWidget()
        self._chapters_table.setColumnCount(3)
        self._chapters_table.setHorizontalHeaderLabels(["Code", "Omschrijving", "Bedrag"])
        self._chapters_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._chapters_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._chapters_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self._chapters_table.verticalHeader().setVisible(False)
        self._chapters_table.setAlternatingRowColors(True)
        self._chapters_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._chapters_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._chapters_table.setMinimumHeight(200)
        self._chapters_table.setStyleSheet("""
            QTableWidget {
                border: none;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QHeaderView::section {
                background: #f5f5f5;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #1a237e;
                font-weight: bold;
            }
        """)
        chapters_layout.addWidget(self._chapters_table)

        layout.addWidget(chapters_group)

        # Opslagen en berekening
        calc_group = QGroupBox("Opslagen en Berekening")
        calc_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
        """)
        calc_layout = QVBoxLayout(calc_group)

        # Berekening tabel
        self._calc_table = QTableWidget()
        self._calc_table.setColumnCount(3)
        self._calc_table.setHorizontalHeaderLabels(["Omschrijving", "%", "Bedrag"])
        self._calc_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._calc_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self._calc_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self._calc_table.verticalHeader().setVisible(False)
        self._calc_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._calc_table.setMinimumHeight(250)
        self._calc_table.setStyleSheet("""
            QTableWidget {
                border: none;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background: #f5f5f5;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #1a237e;
                font-weight: bold;
            }
        """)
        calc_layout.addWidget(self._calc_table)

        layout.addWidget(calc_group)

        # Opslagen invoer
        settings_group = QGroupBox("Opslagen Instellingen")
        settings_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
        """)
        settings_layout = QFormLayout(settings_group)
        settings_layout.setSpacing(12)

        # AK spinbox
        self._ak_spin = QDoubleSpinBox()
        self._ak_spin.setRange(0, 50)
        self._ak_spin.setValue(self._algemene_kosten)
        self._ak_spin.setSuffix(" %")
        self._ak_spin.setDecimals(1)
        self._ak_spin.valueChanged.connect(self._on_ak_changed)
        settings_layout.addRow("Algemene Kosten (AK):", self._ak_spin)

        # W&R spinbox
        self._wr_spin = QDoubleSpinBox()
        self._wr_spin.setRange(0, 50)
        self._wr_spin.setValue(self._winst_risico)
        self._wr_spin.setSuffix(" %")
        self._wr_spin.setDecimals(1)
        self._wr_spin.valueChanged.connect(self._on_wr_changed)
        settings_layout.addRow("Winst & Risico (W&&R):", self._wr_spin)

        # BTW spinbox
        self._btw_spin = QDoubleSpinBox()
        self._btw_spin.setRange(0, 50)
        self._btw_spin.setValue(self._btw_percentage)
        self._btw_spin.setSuffix(" %")
        self._btw_spin.setDecimals(1)
        self._btw_spin.valueChanged.connect(self._on_btw_changed)
        settings_layout.addRow("BTW:", self._btw_spin)

        layout.addWidget(settings_group)

        layout.addStretch()

    def set_schedule(self, schedule: Optional[CostSchedule]):
        """Stel de begroting in"""
        self._schedule = schedule
        self.refresh()

    def refresh(self):
        """Vernieuw de weergave"""
        self._update_chapters_table()
        self._update_calc_table()

    def _update_chapters_table(self):
        """Update de hoofdstukken tabel"""
        self._chapters_table.setRowCount(0)

        if not self._schedule:
            return

        for item in self._schedule.items:
            row = self._chapters_table.rowCount()
            self._chapters_table.insertRow(row)

            # Code
            code_item = QTableWidgetItem(item.identification)
            code_item.setTextAlignment(Qt.AlignCenter)
            self._chapters_table.setItem(row, 0, code_item)

            # Omschrijving
            name_item = QTableWidgetItem(item.name)
            self._chapters_table.setItem(row, 1, name_item)

            # Bedrag
            amount_item = QTableWidgetItem(f"€ {item.subtotal:,.2f}")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self._chapters_table.setItem(row, 2, amount_item)

    def _update_calc_table(self):
        """Update de berekening tabel"""
        self._calc_table.setRowCount(0)

        if not self._schedule:
            return

        directe_kosten = self._schedule.subtotal
        ak_bedrag = directe_kosten * (self._algemene_kosten / 100)
        subtotaal_ak = directe_kosten + ak_bedrag
        wr_bedrag = subtotaal_ak * (self._winst_risico / 100)
        aanneemsom = subtotaal_ak + wr_bedrag
        btw_bedrag = aanneemsom * (self._btw_percentage / 100)
        totaal = aanneemsom + btw_bedrag

        rows = [
            ("Directe bouwkosten", "", directe_kosten, False, False),
            ("Algemene kosten (AK)", f"{self._algemene_kosten:.1f}%", ak_bedrag, False, False),
            ("Subtotaal incl. AK", "", subtotaal_ak, True, False),
            ("Winst & Risico (W&R)", f"{self._winst_risico:.1f}%", wr_bedrag, False, False),
            ("Aanneemsom excl. BTW", "", aanneemsom, True, True),
            ("BTW", f"{self._btw_percentage:.1f}%", btw_bedrag, False, False),
            ("TOTAAL incl. BTW", "", totaal, True, True),
        ]

        for desc, perc, amount, is_bold, is_highlight in rows:
            row = self._calc_table.rowCount()
            self._calc_table.insertRow(row)

            # Omschrijving
            desc_item = QTableWidgetItem(desc)
            if is_bold:
                font = desc_item.font()
                font.setBold(True)
                desc_item.setFont(font)
            if is_highlight:
                desc_item.setBackground(QColor("#e3f2fd"))
            self._calc_table.setItem(row, 0, desc_item)

            # Percentage
            perc_item = QTableWidgetItem(perc)
            perc_item.setTextAlignment(Qt.AlignCenter)
            if is_highlight:
                perc_item.setBackground(QColor("#e3f2fd"))
            self._calc_table.setItem(row, 1, perc_item)

            # Bedrag
            amount_item = QTableWidgetItem(f"€ {amount:,.2f}")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if is_bold:
                font = amount_item.font()
                font.setBold(True)
                amount_item.setFont(font)
            if is_highlight:
                amount_item.setBackground(QColor("#e3f2fd"))
            self._calc_table.setItem(row, 2, amount_item)

        # Pas rijhoogte aan
        self._calc_table.resizeRowsToContents()

    def _on_ak_changed(self, value: float):
        """AK percentage gewijzigd"""
        self._algemene_kosten = value
        self._update_calc_table()
        self.surchargesChanged.emit()

    def _on_wr_changed(self, value: float):
        """W&R percentage gewijzigd"""
        self._winst_risico = value
        self._update_calc_table()
        self.surchargesChanged.emit()

    def _on_btw_changed(self, value: float):
        """BTW percentage gewijzigd"""
        self._btw_percentage = value
        if self._schedule:
            self._schedule.vat_rate = value
        self._update_calc_table()
        self.surchargesChanged.emit()

    @property
    def totaal_incl_btw(self) -> float:
        """Geef het totaal inclusief BTW"""
        if not self._schedule:
            return 0.0
        directe_kosten = self._schedule.subtotal
        ak_bedrag = directe_kosten * (self._algemene_kosten / 100)
        subtotaal_ak = directe_kosten + ak_bedrag
        wr_bedrag = subtotaal_ak * (self._winst_risico / 100)
        aanneemsom = subtotaal_ak + wr_bedrag
        btw_bedrag = aanneemsom * (self._btw_percentage / 100)
        return aanneemsom + btw_bedrag
