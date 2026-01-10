"""
QuotationPanel - Paneel voor offerte instellingen en preview (gecombineerd)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QCheckBox,
    QPushButton, QLabel, QComboBox, QSpinBox, QFrame,
    QLineEdit, QTextEdit, QFormLayout, QScrollArea, QDateEdit,
    QToolButton, QSizePolicy, QSplitter, QTextBrowser,
    QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal, QDate, QLocale
from PySide6.QtGui import QIcon
from PySide6.QtPrintSupport import QPrinter, QPrintDialog


class PaymentTermRow(QFrame):
    """Een rij voor een betalingstermijn"""

    removed = Signal(object)
    changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            PaymentTermRow {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                padding: 4px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        # Percentage
        self._percentage = QSpinBox()
        self._percentage.setMinimum(0)
        self._percentage.setMaximum(100)
        self._percentage.setValue(0)
        self._percentage.setSuffix("%")
        self._percentage.setMinimumWidth(70)
        self._percentage.valueChanged.connect(self.changed.emit)
        layout.addWidget(self._percentage)

        # Omschrijving
        self._description = QLineEdit()
        self._description.setPlaceholderText("Omschrijving (bijv. 'Bij opdracht', 'Bij oplevering')")
        self._description.textChanged.connect(self.changed.emit)
        layout.addWidget(self._description, 1)

        # Optionele datum
        self._use_date = QCheckBox("Datum:")
        self._use_date.setChecked(False)
        self._use_date.toggled.connect(self._on_date_toggle)
        layout.addWidget(self._use_date)

        self._date = QDateEdit()
        self._date.setDate(QDate.currentDate())
        self._date.setCalendarPopup(True)
        self._date.setEnabled(False)
        self._date.dateChanged.connect(self.changed.emit)
        layout.addWidget(self._date)

        # Verwijder knop
        remove_btn = QToolButton()
        remove_btn.setText("X")
        remove_btn.setStyleSheet("""
            QToolButton {
                background-color: #fee2e2;
                color: #dc2626;
                border: 1px solid #fca5a5;
                border-radius: 3px;
                padding: 2px 6px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #fecaca;
            }
        """)
        remove_btn.clicked.connect(lambda: self.removed.emit(self))
        layout.addWidget(remove_btn)

    def _on_date_toggle(self, checked: bool):
        """Toggle datum veld"""
        self._date.setEnabled(checked)
        self.changed.emit()

    def get_data(self) -> dict:
        """Haal termijn gegevens op"""
        data = {
            "percentage": self._percentage.value(),
            "description": self._description.text(),
        }
        if self._use_date.isChecked():
            data["date"] = self._date.date().toString("yyyy-MM-dd")
        return data

    def set_data(self, data: dict):
        """Stel termijn gegevens in"""
        self._percentage.setValue(data.get("percentage", 0))
        self._description.setText(data.get("description", ""))
        if "date" in data:
            self._use_date.setChecked(True)
            self._date.setDate(QDate.fromString(data["date"], "yyyy-MM-dd"))


class QuotationPanel(QWidget):
    """Paneel voor offerte instellingen, preview en losse onderdelen"""

    generateQuotation = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._payment_term_rows = []
        self._schedule = None
        self._project_data = {}
        self._locale = QLocale(QLocale.Dutch, QLocale.Netherlands)
        self._setup_ui()

    def _setup_ui(self):
        """Stel de UI in"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Splitter voor links (opties) en rechts (preview)
        splitter = QSplitter(Qt.Horizontal)

        # =========== LINKER PANEEL: OPTIES ===========
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)

        # Scroll area voor opties
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setMaximumWidth(450)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(15)

        # Offerte details groep
        details_group = QGroupBox("Offerte Details")
        details_form = QFormLayout(details_group)

        self._quotation_number = QLineEdit()
        self._quotation_number.setPlaceholderText("Offertenummer")
        details_form.addRow("Offertenummer:", self._quotation_number)

        self._quotation_date = QDateEdit()
        self._quotation_date.setDate(QDate.currentDate())
        self._quotation_date.setCalendarPopup(True)
        details_form.addRow("Datum:", self._quotation_date)

        self._validity_days = QSpinBox()
        self._validity_days.setMinimum(7)
        self._validity_days.setMaximum(365)
        self._validity_days.setValue(30)
        self._validity_days.setSuffix(" dagen")
        details_form.addRow("Geldigheid:", self._validity_days)

        self._reference = QLineEdit()
        self._reference.setPlaceholderText("Uw referentie/kenmerk")
        details_form.addRow("Referentie:", self._reference)

        content_layout.addWidget(details_group)

        # Inhoud opties groep
        content_group = QGroupBox("Inhoud")
        content_form = QVBoxLayout(content_group)

        self._show_detail = QCheckBox("Gedetailleerde specificatie tonen")
        self._show_detail.setChecked(True)
        content_form.addWidget(self._show_detail)

        self._show_quantities = QCheckBox("Hoeveelheden tonen")
        self._show_quantities.setChecked(True)
        content_form.addWidget(self._show_quantities)

        self._show_unit_prices = QCheckBox("Eenheidsprijzen tonen")
        self._show_unit_prices.setChecked(False)
        content_form.addWidget(self._show_unit_prices)

        self._show_vat_spec = QCheckBox("BTW specificatie tonen")
        self._show_vat_spec.setChecked(True)
        content_form.addWidget(self._show_vat_spec)

        self._include_terms = QCheckBox("Algemene voorwaarden bijvoegen")
        self._include_terms.setChecked(True)
        content_form.addWidget(self._include_terms)

        content_layout.addWidget(content_group)

        # Teksten groep
        texts_group = QGroupBox("Teksten")
        texts_form = QFormLayout(texts_group)

        self._intro_text = QTextEdit()
        self._intro_text.setPlaceholderText(
            "Introductietekst voor de offerte...\n"
            "Bijv: Hierbij ontvangt u onze offerte voor het project..."
        )
        self._intro_text.setMaximumHeight(60)
        texts_form.addRow("Inleiding:", self._intro_text)

        self._closing_text = QTextEdit()
        self._closing_text.setPlaceholderText(
            "Afsluitende tekst...\n"
            "Bijv: Wij vertrouwen u hiermee een passende aanbieding te hebben gedaan..."
        )
        self._closing_text.setMaximumHeight(60)
        texts_form.addRow("Afsluiting:", self._closing_text)

        content_layout.addWidget(texts_group)

        # Betaalvoorwaarden groep (optioneel en uitklapbaar)
        self._payment_group = QGroupBox("Betaalvoorwaarden")
        self._payment_group.setCheckable(True)
        self._payment_group.setChecked(True)
        payment_main_layout = QVBoxLayout(self._payment_group)

        # Keuze: standaard of custom
        self._use_standard_payment = QCheckBox("Standaard schema")
        self._use_standard_payment.setChecked(True)
        self._use_standard_payment.toggled.connect(self._on_payment_type_toggle)
        payment_main_layout.addWidget(self._use_standard_payment)

        # Standaard dropdown
        self._standard_payment_container = QWidget()
        standard_layout = QHBoxLayout(self._standard_payment_container)
        standard_layout.setContentsMargins(20, 0, 0, 0)
        self._payment_type = QComboBox()
        self._payment_type.addItems([
            "100% bij oplevering",
            "50% vooruit, 50% bij oplevering",
            "30% vooruit, 40% halverwege, 30% bij oplevering",
            "Termijnen volgens bestek"
        ])
        standard_layout.addWidget(self._payment_type)
        payment_main_layout.addWidget(self._standard_payment_container)

        # Custom termijnen
        self._use_custom_terms = QCheckBox("Aangepaste termijnen")
        self._use_custom_terms.toggled.connect(self._on_custom_terms_toggle)
        payment_main_layout.addWidget(self._use_custom_terms)

        self._custom_terms_container = QWidget()
        self._custom_terms_container.setVisible(False)
        custom_layout = QVBoxLayout(self._custom_terms_container)
        custom_layout.setContentsMargins(0, 0, 0, 0)

        self._terms_rows_container = QWidget()
        self._terms_rows_layout = QVBoxLayout(self._terms_rows_container)
        self._terms_rows_layout.setContentsMargins(0, 0, 0, 0)
        self._terms_rows_layout.setSpacing(4)
        custom_layout.addWidget(self._terms_rows_container)

        add_term_btn = QPushButton("+ Termijn toevoegen")
        add_term_btn.clicked.connect(self._add_payment_term)
        custom_layout.addWidget(add_term_btn)

        self._total_percentage_label = QLabel("Totaal: 0%")
        custom_layout.addWidget(self._total_percentage_label)

        # Presets
        presets_layout = QHBoxLayout()
        presets_layout.addWidget(QLabel("Snelkeuze:"))
        for preset_name, preset_data in [
            ("50/50", [{"percentage": 50, "description": "Bij opdracht"}, {"percentage": 50, "description": "Bij oplevering"}]),
            ("30/40/30", [{"percentage": 30, "description": "Bij opdracht"}, {"percentage": 40, "description": "Halverwege"}, {"percentage": 30, "description": "Bij oplevering"}]),
        ]:
            btn = QPushButton(preset_name)
            btn.setMaximumWidth(70)
            btn.clicked.connect(lambda checked, d=preset_data: self._apply_preset(d))
            presets_layout.addWidget(btn)
        presets_layout.addStretch()
        custom_layout.addLayout(presets_layout)

        payment_main_layout.addWidget(self._custom_terms_container)

        # Betaaltermijn dagen
        days_layout = QHBoxLayout()
        days_layout.addWidget(QLabel("Factuurtermijn:"))
        self._payment_days = QSpinBox()
        self._payment_days.setMinimum(7)
        self._payment_days.setMaximum(90)
        self._payment_days.setValue(30)
        self._payment_days.setSuffix(" dagen")
        days_layout.addWidget(self._payment_days)
        days_layout.addStretch()
        payment_main_layout.addLayout(days_layout)

        content_layout.addWidget(self._payment_group)

        # =========== LOSSE ONDERDELEN TABEL ===========
        parts_group = QGroupBox("Losse Onderdelen / Meerwerk")
        parts_group.setCheckable(True)
        parts_group.setChecked(False)
        parts_layout = QVBoxLayout(parts_group)

        self._parts_table = QTableWidget()
        self._parts_table.setColumnCount(6)
        self._parts_table.setHorizontalHeaderLabels([
            "Code", "Omschrijving", "Eenh.", "Hoev.", "Prijs", "Totaal"
        ])
        self._parts_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._parts_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._parts_table.setMinimumHeight(120)
        self._parts_table.setMaximumHeight(200)
        parts_layout.addWidget(self._parts_table)

        parts_buttons = QHBoxLayout()
        add_part_btn = QPushButton("+ Onderdeel toevoegen")
        add_part_btn.clicked.connect(self._add_loose_part)
        parts_buttons.addWidget(add_part_btn)

        remove_part_btn = QPushButton("- Verwijderen")
        remove_part_btn.clicked.connect(self._remove_loose_part)
        parts_buttons.addWidget(remove_part_btn)
        parts_buttons.addStretch()
        parts_layout.addLayout(parts_buttons)

        # IFC Type selectie voor onderdelen
        ifc_type_layout = QHBoxLayout()
        ifc_type_layout.addWidget(QLabel("IFC Type:"))
        self._ifc_type_combo = QComboBox()
        self._ifc_type_combo.addItems([
            "IfcBuildingElementProxy",
            "IfcWall",
            "IfcSlab",
            "IfcBeam",
            "IfcColumn",
            "IfcDoor",
            "IfcWindow",
            "IfcStair",
            "IfcRoof",
            "IfcCovering",
            "IfcFurnishingElement"
        ])
        ifc_type_layout.addWidget(self._ifc_type_combo)
        ifc_type_layout.addStretch()
        parts_layout.addLayout(ifc_type_layout)

        content_layout.addWidget(parts_group)
        self._parts_group = parts_group

        content_layout.addStretch()
        scroll.setWidget(content)
        left_layout.addWidget(scroll)

        # Genereer knop
        generate_btn = QPushButton("Offerte Genereren")
        generate_btn.setMinimumHeight(40)
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #22c55e;
                color: white;
                font-weight: bold;
                font-size: 11pt;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #16a34a;
            }
        """)
        generate_btn.clicked.connect(self._generate_quotation)
        left_layout.addWidget(generate_btn)

        splitter.addWidget(left_panel)

        # =========== RECHTER PANEEL: PREVIEW ===========
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Preview toolbar
        preview_toolbar = QFrame()
        preview_toolbar.setStyleSheet("background: #f1f5f9; border-bottom: 1px solid #e2e8f0;")
        toolbar_layout = QHBoxLayout(preview_toolbar)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)

        toolbar_layout.addWidget(QLabel("Offerte Preview"))
        toolbar_layout.addStretch()

        print_btn = QPushButton("Afdrukken")
        print_btn.clicked.connect(self._print_quotation)
        toolbar_layout.addWidget(print_btn)

        pdf_btn = QPushButton("PDF Exporteren")
        pdf_btn.setStyleSheet("background-color: #ef4444; color: white;")
        pdf_btn.clicked.connect(self._export_pdf)
        toolbar_layout.addWidget(pdf_btn)

        right_layout.addWidget(preview_toolbar)

        # Preview area
        preview_frame = QFrame()
        preview_frame.setStyleSheet("background: #64748b;")
        preview_frame_layout = QVBoxLayout(preview_frame)
        preview_frame_layout.setContentsMargins(30, 20, 30, 20)

        self._preview = QTextBrowser()
        self._preview.setStyleSheet("background: white; border: none;")
        self._preview.setOpenExternalLinks(False)
        self._set_placeholder()

        preview_frame_layout.addWidget(self._preview)
        right_layout.addWidget(preview_frame, 1)

        splitter.addWidget(right_panel)

        # Stel splitter verhoudingen in
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([400, 800])

        layout.addWidget(splitter)

    def _set_placeholder(self):
        """Placeholder voor preview"""
        self._preview.setHtml("""
            <div style="text-align: center; padding: 50px; color: #94a3b8;">
                <h2 style="color: #64748b;">Offerte Preview</h2>
                <p>Klik op "Offerte Genereren" om een voorbeeld te zien.</p>
            </div>
        """)

    def set_schedule(self, schedule):
        """Stel de begroting in"""
        self._schedule = schedule

    def set_project_data(self, data: dict):
        """Stel projectgegevens in"""
        self._project_data = data

    def _on_payment_type_toggle(self, checked: bool):
        self._standard_payment_container.setVisible(checked)
        if checked:
            self._use_custom_terms.setChecked(False)

    def _on_custom_terms_toggle(self, checked: bool):
        self._custom_terms_container.setVisible(checked)
        if checked:
            self._use_standard_payment.setChecked(False)
            self._standard_payment_container.setVisible(False)
            if not self._payment_term_rows:
                self._add_payment_term()

    def _add_payment_term(self):
        row = PaymentTermRow()
        row.removed.connect(self._remove_payment_term)
        row.changed.connect(self._update_total_percentage)
        self._terms_rows_layout.addWidget(row)
        self._payment_term_rows.append(row)
        self._update_total_percentage()

    def _remove_payment_term(self, row):
        if row in self._payment_term_rows:
            self._payment_term_rows.remove(row)
            row.deleteLater()
            self._update_total_percentage()

    def _update_total_percentage(self):
        total = sum(row._percentage.value() for row in self._payment_term_rows)
        if total == 100:
            self._total_percentage_label.setText("Totaal: 100% OK")
            self._total_percentage_label.setStyleSheet("color: #16a34a; font-weight: bold;")
        elif total > 100:
            self._total_percentage_label.setText(f"Totaal: {total}% (te veel!)")
            self._total_percentage_label.setStyleSheet("color: #dc2626; font-weight: bold;")
        else:
            self._total_percentage_label.setText(f"Totaal: {total}% (nog {100-total}%)")
            self._total_percentage_label.setStyleSheet("color: #ea580c;")

    def _apply_preset(self, terms: list):
        for row in self._payment_term_rows[:]:
            self._remove_payment_term(row)
        for term_data in terms:
            row = PaymentTermRow()
            row.removed.connect(self._remove_payment_term)
            row.changed.connect(self._update_total_percentage)
            row.set_data(term_data)
            self._terms_rows_layout.addWidget(row)
            self._payment_term_rows.append(row)
        self._update_total_percentage()

    # =========== LOSSE ONDERDELEN ===========

    def _add_loose_part(self):
        """Voeg een los onderdeel toe"""
        row = self._parts_table.rowCount()
        self._parts_table.insertRow(row)

        # Code
        self._parts_table.setItem(row, 0, QTableWidgetItem(f"M{row+1:03d}"))
        # Omschrijving
        self._parts_table.setItem(row, 1, QTableWidgetItem("Nieuw onderdeel"))
        # Eenheid
        self._parts_table.setItem(row, 2, QTableWidgetItem("st"))
        # Hoeveelheid
        qty_item = QTableWidgetItem("1")
        qty_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._parts_table.setItem(row, 3, qty_item)
        # Prijs
        price_item = QTableWidgetItem("0.00")
        price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._parts_table.setItem(row, 4, price_item)
        # Totaal
        total_item = QTableWidgetItem("0.00")
        total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        total_item.setFlags(total_item.flags() & ~Qt.ItemIsEditable)
        self._parts_table.setItem(row, 5, total_item)

        # Connect cell changed
        self._parts_table.cellChanged.connect(self._update_part_total)

    def _remove_loose_part(self):
        """Verwijder geselecteerd onderdeel"""
        selected = self._parts_table.selectedItems()
        if selected:
            row = selected[0].row()
            self._parts_table.removeRow(row)

    def _update_part_total(self, row, col):
        """Update totaal voor een onderdeel"""
        if col in [3, 4]:  # Hoeveelheid of prijs gewijzigd
            try:
                qty = float(self._parts_table.item(row, 3).text().replace(',', '.'))
                price = float(self._parts_table.item(row, 4).text().replace(',', '.'))
                total = qty * price
                self._parts_table.item(row, 5).setText(f"{total:.2f}")
            except (ValueError, AttributeError):
                pass

    def get_loose_parts(self) -> list:
        """Haal losse onderdelen op"""
        parts = []
        for row in range(self._parts_table.rowCount()):
            try:
                parts.append({
                    "code": self._parts_table.item(row, 0).text(),
                    "description": self._parts_table.item(row, 1).text(),
                    "unit": self._parts_table.item(row, 2).text(),
                    "quantity": float(self._parts_table.item(row, 3).text().replace(',', '.')),
                    "price": float(self._parts_table.item(row, 4).text().replace(',', '.')),
                    "ifc_type": self._ifc_type_combo.currentText()
                })
            except (ValueError, AttributeError):
                pass
        return parts

    # =========== GENEREREN EN EXPORT ===========

    def _generate_quotation(self):
        """Genereer de offerte"""
        html = self._generate_quotation_html()
        self._preview.setHtml(html)
        self.generateQuotation.emit()

    def _generate_quotation_html(self) -> str:
        """Genereer offerte HTML"""
        css = """
        <style>
            body { font-family: 'Segoe UI', Arial; font-size: 10pt; color: #1e293b; margin: 30px; }
            .header { border-bottom: 2px solid #0ea5e9; padding-bottom: 15px; margin-bottom: 20px; }
            h1 { color: #0ea5e9; font-size: 18pt; margin: 0; }
            h2 { color: #334155; font-size: 14pt; border-bottom: 1px solid #e2e8f0; padding-bottom: 5px; }
            table { width: 100%; border-collapse: collapse; margin: 10px 0; }
            th { background: #f1f5f9; text-align: left; padding: 8px; border: 1px solid #e2e8f0; }
            td { padding: 6px 8px; border: 1px solid #e2e8f0; }
            .number { text-align: right; }
            .total-row { background: #0ea5e9; color: white; font-weight: bold; }
            .intro { background: #f8fafc; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
            .closing { margin-top: 30px; font-style: italic; }
            .payment-terms { background: #fef3c7; padding: 15px; border-radius: 4px; margin-top: 20px; }
        </style>
        """

        html = f"<!DOCTYPE html><html><head>{css}</head><body>"

        # Header
        html += '<div class="header">'
        html += f'<h1>OFFERTE</h1>'
        html += f'<p><strong>Offertenummer:</strong> {self._quotation_number.text() or "..."}</p>'
        html += f'<p><strong>Datum:</strong> {self._quotation_date.date().toString("dd-MM-yyyy")}</p>'
        html += f'<p><strong>Geldig tot:</strong> {self._quotation_date.date().addDays(self._validity_days.value()).toString("dd-MM-yyyy")}</p>'
        if self._reference.text():
            html += f'<p><strong>Uw referentie:</strong> {self._reference.text()}</p>'
        html += '</div>'

        # Intro tekst
        if self._intro_text.toPlainText():
            html += f'<div class="intro">{self._intro_text.toPlainText()}</div>'

        # Begroting tabel
        if self._schedule:
            html += "<h2>Specificatie</h2>"
            html += "<table><tr><th>Code</th><th>Omschrijving</th>"
            if self._show_quantities.isChecked():
                html += "<th>Eenh.</th><th class='number'>Hoev.</th>"
            if self._show_unit_prices.isChecked():
                html += "<th class='number'>Prijs</th>"
            html += "<th class='number'>Totaal</th></tr>"

            for item in self._schedule.items:
                html += self._render_item_row(item, 0)

            html += "</table>"

            # Totalen
            subtotal = self._schedule.subtotal
            vat = subtotal * 0.21
            total = subtotal + vat

            html += "<table style='width: 300px; margin-left: auto; margin-top: 20px;'>"
            html += f"<tr><td>Subtotaal</td><td class='number'>{self._format_currency(subtotal)}</td></tr>"
            if self._show_vat_spec.isChecked():
                html += f"<tr><td>BTW 21%</td><td class='number'>{self._format_currency(vat)}</td></tr>"
            html += f"<tr class='total-row'><td>Totaal</td><td class='number'>{self._format_currency(total)}</td></tr>"
            html += "</table>"

        # Losse onderdelen
        parts = self.get_loose_parts()
        if parts and self._parts_group.isChecked():
            html += "<h2>Losse Onderdelen / Meerwerk</h2>"
            html += "<table><tr><th>Code</th><th>Omschrijving</th><th>Eenh.</th>"
            html += "<th class='number'>Hoev.</th><th class='number'>Prijs</th><th class='number'>Totaal</th></tr>"
            parts_total = 0
            for part in parts:
                line_total = part['quantity'] * part['price']
                parts_total += line_total
                html += f"<tr><td>{part['code']}</td><td>{part['description']}</td><td>{part['unit']}</td>"
                html += f"<td class='number'>{part['quantity']:.2f}</td>"
                html += f"<td class='number'>{self._format_currency(part['price'])}</td>"
                html += f"<td class='number'>{self._format_currency(line_total)}</td></tr>"
            html += f"<tr style='font-weight: bold;'><td colspan='5'>Totaal onderdelen</td>"
            html += f"<td class='number'>{self._format_currency(parts_total)}</td></tr>"
            html += "</table>"

        # Betaalvoorwaarden
        if self._payment_group.isChecked():
            html += '<div class="payment-terms">'
            html += '<strong>Betaalvoorwaarden:</strong><br>'
            if self._use_standard_payment.isChecked():
                html += f'{self._payment_type.currentText()}<br>'
            elif self._use_custom_terms.isChecked():
                for row in self._payment_term_rows:
                    data = row.get_data()
                    html += f'- {data["percentage"]}% {data["description"]}'
                    if 'date' in data:
                        html += f' (datum: {data["date"]})'
                    html += '<br>'
            html += f'Betaaltermijn facturen: {self._payment_days.value()} dagen'
            html += '</div>'

        # Afsluiting
        if self._closing_text.toPlainText():
            html += f'<div class="closing">{self._closing_text.toPlainText()}</div>'

        html += "</body></html>"
        return html

    def _render_item_row(self, item, level: int) -> str:
        html = ""
        indent = "&nbsp;" * (level * 4)
        is_chapter = len(item.children) > 0

        if self._show_detail.isChecked() or is_chapter:
            style = "font-weight: bold; background: #e0f2fe;" if is_chapter else ""
            html += f"<tr style='{style}'>"
            html += f"<td>{item.identification}</td>"
            html += f"<td>{indent}{item.name}</td>"

            if self._show_quantities.isChecked():
                if not is_chapter:
                    html += f"<td>{item.unit_symbol}</td>"
                    html += f"<td class='number'>{self._locale.toString(item.quantity, 'f', 2)}</td>"
                else:
                    html += "<td></td><td></td>"

            if self._show_unit_prices.isChecked():
                if not is_chapter:
                    html += f"<td class='number'>{self._format_currency(item.unit_price)}</td>"
                else:
                    html += "<td></td>"

            html += f"<td class='number'>{self._format_currency(item.subtotal)}</td>"
            html += "</tr>"

        if self._show_detail.isChecked():
            for child in item.children:
                html += self._render_item_row(child, level + 1)

        return html

    def _format_currency(self, value: float) -> str:
        return f"&euro; {self._locale.toString(value, 'f', 2)}"

    def _print_quotation(self):
        """Print de offerte"""
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QPrintDialog.Accepted:
            self._preview.document().print_(printer)

    def _export_pdf(self):
        """Exporteer naar PDF"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Offerte Exporteren als PDF",
            f"Offerte_{self._quotation_number.text() or 'nieuw'}.pdf",
            "PDF Bestanden (*.pdf)"
        )
        if file_path:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(file_path)
            self._preview.document().print_(printer)
            QMessageBox.information(self, "Export Voltooid", f"Offerte geexporteerd naar:\n{file_path}")

    def get_quotation_data(self) -> dict:
        """Haal alle offerte gegevens op"""
        data = {
            "quotation_number": self._quotation_number.text(),
            "quotation_date": self._quotation_date.date().toString("yyyy-MM-dd"),
            "validity_days": self._validity_days.value(),
            "reference": self._reference.text(),
            "show_detail": self._show_detail.isChecked(),
            "show_quantities": self._show_quantities.isChecked(),
            "show_unit_prices": self._show_unit_prices.isChecked(),
            "show_vat_spec": self._show_vat_spec.isChecked(),
            "include_terms": self._include_terms.isChecked(),
            "intro_text": self._intro_text.toPlainText(),
            "closing_text": self._closing_text.toPlainText(),
            "include_payment_terms": self._payment_group.isChecked(),
            "payment_days": self._payment_days.value(),
            "loose_parts": self.get_loose_parts(),
        }

        if self._payment_group.isChecked():
            if self._use_standard_payment.isChecked():
                data["payment_type"] = "standard"
                data["payment_schema"] = self._payment_type.currentText()
            elif self._use_custom_terms.isChecked():
                data["payment_type"] = "custom"
                data["custom_terms"] = [row.get_data() for row in self._payment_term_rows]

        return data
