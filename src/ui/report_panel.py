"""
ReportPanel - Paneel voor rapportage generatie met koptekst/voettekst en orientatie
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QCheckBox,
    QPushButton, QLabel, QComboBox, QSpinBox, QFrame,
    QTextBrowser, QScrollArea, QLineEdit, QFormLayout,
    QRadioButton, QButtonGroup, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QLocale
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from typing import Optional


class ReportPanel(QWidget):
    """Paneel voor het genereren en bekijken van rapporten"""

    generateReport = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._schedule = None
        self._project_data = {}
        self._locale = QLocale(QLocale.Dutch, QLocale.Netherlands)
        self._setup_ui()

    def _setup_ui(self):
        """Stel de UI in"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Linker kolom: Opties
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_panel.setMaximumWidth(350)

        # Rapport opties groep
        options_group = QGroupBox("Rapport Opties")
        options_layout = QVBoxLayout(options_group)

        # Type rapport
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        self._report_type = QComboBox()
        self._report_type.addItems([
            "Volledige begroting",
            "Samenvatting per hoofdstuk",
            "Alleen hoofdstukken",
            "Gedetailleerd met specificaties"
        ])
        type_layout.addWidget(self._report_type)
        options_layout.addLayout(type_layout)

        # Checkboxes voor onderdelen
        self._include_project = QCheckBox("Projectgegevens opnemen")
        self._include_project.setChecked(True)
        options_layout.addWidget(self._include_project)

        self._include_surcharges = QCheckBox("Opslagen tonen")
        self._include_surcharges.setChecked(True)
        options_layout.addWidget(self._include_surcharges)

        self._include_vat = QCheckBox("BTW specificatie tonen")
        self._include_vat.setChecked(True)
        options_layout.addWidget(self._include_vat)

        self._include_quantities = QCheckBox("Hoeveelheden tonen")
        self._include_quantities.setChecked(True)
        options_layout.addWidget(self._include_quantities)

        self._include_unit_prices = QCheckBox("Eenheidsprijzen tonen")
        self._include_unit_prices.setChecked(True)
        options_layout.addWidget(self._include_unit_prices)

        self._include_sfb = QCheckBox("SFB-codering tonen")
        self._include_sfb.setChecked(False)
        options_layout.addWidget(self._include_sfb)

        left_layout.addWidget(options_group)

        # Pagina orientatie groep
        orientation_group = QGroupBox("Pagina Orientatie")
        orientation_layout = QVBoxLayout(orientation_group)

        self._orientation_group = QButtonGroup(self)

        self._portrait_radio = QRadioButton("Staand (Portrait)")
        self._portrait_radio.setChecked(True)
        self._orientation_group.addButton(self._portrait_radio)
        orientation_layout.addWidget(self._portrait_radio)

        self._landscape_radio = QRadioButton("Liggend (Landscape)")
        self._orientation_group.addButton(self._landscape_radio)
        orientation_layout.addWidget(self._landscape_radio)

        left_layout.addWidget(orientation_group)

        # Koptekst/Voettekst groep
        header_footer_group = QGroupBox("Koptekst / Voettekst")
        hf_layout = QFormLayout(header_footer_group)

        self._header_left = QLineEdit()
        self._header_left.setPlaceholderText("Bijv. Bedrijfsnaam")
        hf_layout.addRow("Koptekst links:", self._header_left)

        self._header_center = QLineEdit()
        self._header_center.setPlaceholderText("Bijv. Projectnaam")
        hf_layout.addRow("Koptekst midden:", self._header_center)

        self._header_right = QLineEdit()
        self._header_right.setPlaceholderText("Bijv. Datum")
        hf_layout.addRow("Koptekst rechts:", self._header_right)

        self._footer_left = QLineEdit()
        self._footer_left.setPlaceholderText("Bijv. Vertrouwelijk")
        hf_layout.addRow("Voettekst links:", self._footer_left)

        self._footer_center = QLineEdit()
        self._footer_center.setPlaceholderText("Bijv. Pagina {page}")
        self._footer_center.setText("Pagina {page} van {pages}")
        hf_layout.addRow("Voettekst midden:", self._footer_center)

        self._footer_right = QLineEdit()
        self._footer_right.setPlaceholderText("Bijv. Versie 1.0")
        hf_layout.addRow("Voettekst rechts:", self._footer_right)

        left_layout.addWidget(header_footer_group)

        # Knoppen
        buttons_layout = QVBoxLayout()

        generate_btn = QPushButton("Voorbeeld Genereren")
        generate_btn.setMinimumHeight(40)
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #0ea5e9;
                color: white;
                font-weight: bold;
                font-size: 11pt;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0284c7;
            }
        """)
        generate_btn.clicked.connect(self._generate_preview)
        buttons_layout.addWidget(generate_btn)

        export_pdf_btn = QPushButton("Exporteren als PDF")
        export_pdf_btn.clicked.connect(self._export_pdf)
        buttons_layout.addWidget(export_pdf_btn)

        print_btn = QPushButton("Afdrukken")
        print_btn.clicked.connect(self._print_report)
        buttons_layout.addWidget(print_btn)

        left_layout.addLayout(buttons_layout)
        left_layout.addStretch()

        layout.addWidget(left_panel)

        # Rechter kolom: Preview
        preview_group = QGroupBox("Voorbeeld")
        preview_layout = QVBoxLayout(preview_group)

        self._preview = QTextBrowser()
        self._preview.setMinimumWidth(500)
        self._preview.setOpenExternalLinks(False)
        self._set_placeholder()

        preview_layout.addWidget(self._preview)

        layout.addWidget(preview_group, 1)

    def _set_placeholder(self):
        """Stel placeholder content in"""
        self._preview.setHtml("""
            <div style="text-align: center; padding: 50px; color: #94a3b8;">
                <h2 style="color: #64748b;">Rapport Voorbeeld</h2>
                <p>Klik op "Voorbeeld Genereren" om een voorbeeld te zien.</p>
                <p>Zorg dat er een begroting geladen is.</p>
            </div>
        """)

    def set_schedule(self, schedule):
        """Stel de begroting in"""
        self._schedule = schedule

    def set_project_data(self, data: dict):
        """Stel projectgegevens in"""
        self._project_data = data
        # Vul header velden automatisch in
        if data.get("project_name") and not self._header_center.text():
            self._header_center.setText(data.get("project_name", ""))
        if data.get("contractor_name") and not self._header_left.text():
            self._header_left.setText(data.get("contractor_name", ""))

    def _generate_preview(self):
        """Genereer het rapport voorbeeld"""
        if not self._schedule:
            self._preview.setHtml("""
                <div style="text-align: center; padding: 50px; color: #ef4444;">
                    <h2>Geen begroting geladen</h2>
                    <p>Open eerst een begroting om een rapport te genereren.</p>
                </div>
            """)
            return

        html = self._generate_report_html()
        self._preview.setHtml(html)
        self.generateReport.emit()

    def _generate_report_html(self) -> str:
        """Genereer de HTML voor het rapport"""
        options = self.get_options()

        # CSS Styling
        css = """
        <style>
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
                color: #1e293b;
                margin: 20px;
            }
            .header {
                border-bottom: 2px solid #0ea5e9;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }
            .header-row {
                display: flex;
                justify-content: space-between;
            }
            .header-left { text-align: left; }
            .header-center { text-align: center; flex-grow: 1; }
            .header-right { text-align: right; }
            h1 {
                color: #0ea5e9;
                font-size: 18pt;
                margin: 0 0 10px 0;
            }
            h2 {
                color: #334155;
                font-size: 14pt;
                border-bottom: 1px solid #e2e8f0;
                padding-bottom: 5px;
                margin-top: 20px;
            }
            h3 {
                color: #475569;
                font-size: 12pt;
                margin: 15px 0 10px 0;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 10px 0;
            }
            th {
                background-color: #f1f5f9;
                color: #334155;
                text-align: left;
                padding: 8px;
                border: 1px solid #e2e8f0;
                font-weight: 600;
            }
            td {
                padding: 6px 8px;
                border: 1px solid #e2e8f0;
            }
            tr:nth-child(even) {
                background-color: #f8fafc;
            }
            .chapter-row {
                background-color: #e0f2fe !important;
                font-weight: bold;
            }
            .number { text-align: right; }
            .total-row {
                background-color: #0ea5e9 !important;
                color: white;
                font-weight: bold;
            }
            .subtotal-row {
                background-color: #f1f5f9;
                font-weight: bold;
            }
            .project-info {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 20px;
            }
            .info-block {
                background-color: #f8fafc;
                padding: 15px;
                border-radius: 4px;
                border: 1px solid #e2e8f0;
            }
            .info-block h3 {
                margin-top: 0;
                color: #0ea5e9;
            }
            .info-row {
                margin: 5px 0;
            }
            .info-label {
                color: #64748b;
                font-size: 9pt;
            }
            .footer {
                margin-top: 30px;
                padding-top: 10px;
                border-top: 1px solid #e2e8f0;
                font-size: 9pt;
                color: #64748b;
            }
        </style>
        """

        html = f"<!DOCTYPE html><html><head>{css}</head><body>"

        # Header
        html += '<div class="header">'
        html += '<table style="border: none; width: 100%;"><tr>'
        html += f'<td style="border: none; text-align: left; width: 33%;">{self._header_left.text()}</td>'
        html += f'<td style="border: none; text-align: center; width: 34%;"><strong>{self._header_center.text()}</strong></td>'
        html += f'<td style="border: none; text-align: right; width: 33%;">{self._header_right.text()}</td>'
        html += '</tr></table>'
        html += '</div>'

        # Titel
        html += f"<h1>{self._schedule.name}</h1>"

        # Projectgegevens
        if options["include_project"] and self._project_data:
            html += '<div class="project-info">'

            # Project info
            html += '<div class="info-block">'
            html += '<h3>Projectinformatie</h3>'
            if self._project_data.get("project_name"):
                html += f'<div class="info-row"><span class="info-label">Project:</span> {self._project_data["project_name"]}</div>'
            if self._project_data.get("project_number"):
                html += f'<div class="info-row"><span class="info-label">Nummer:</span> {self._project_data["project_number"]}</div>'
            if self._project_data.get("project_location"):
                html += f'<div class="info-row"><span class="info-label">Locatie:</span> {self._project_data["project_location"]}</div>'
            if self._project_data.get("project_date"):
                html += f'<div class="info-row"><span class="info-label">Datum:</span> {self._project_data["project_date"]}</div>'
            html += '</div>'

            # Opdrachtgever info
            html += '<div class="info-block">'
            html += '<h3>Opdrachtgever</h3>'
            if self._project_data.get("client_name"):
                html += f'<div class="info-row">{self._project_data["client_name"]}</div>'
            if self._project_data.get("client_address"):
                html += f'<div class="info-row">{self._project_data["client_address"]}</div>'
            if self._project_data.get("client_postal"):
                html += f'<div class="info-row">{self._project_data["client_postal"]}</div>'
            if self._project_data.get("client_contact"):
                html += f'<div class="info-row"><span class="info-label">Contact:</span> {self._project_data["client_contact"]}</div>'
            html += '</div>'

            html += '</div>'

        # Begroting tabel
        html += "<h2>Begroting</h2>"
        html += "<table>"

        # Header rij
        html += "<tr>"
        html += "<th>Code</th>"
        if options["include_sfb"]:
            html += "<th>SFB</th>"
        html += "<th>Omschrijving</th>"
        if options["include_quantities"]:
            html += "<th>Eenh.</th>"
            html += "<th class='number'>Hoev.</th>"
        if options["include_unit_prices"]:
            html += "<th class='number'>Prijs</th>"
        html += "<th class='number'>Totaal</th>"
        html += "</tr>"

        # Items
        for item in self._schedule.items:
            html += self._render_item_row(item, options, 0)

        html += "</table>"

        # Totalen
        subtotal = self._schedule.subtotal
        vat_rate = getattr(self._schedule, 'vat_rate', 21)
        vat = subtotal * (vat_rate / 100)
        total = subtotal + vat

        html += "<table style='width: 300px; margin-left: auto; margin-top: 20px;'>"
        html += f"<tr class='subtotal-row'><td>Subtotaal</td><td class='number'>{self._format_currency(subtotal)}</td></tr>"
        if options["include_vat"]:
            html += f"<tr><td>BTW ({vat_rate}%)</td><td class='number'>{self._format_currency(vat)}</td></tr>"
        html += f"<tr class='total-row'><td>Totaal</td><td class='number'>{self._format_currency(total)}</td></tr>"
        html += "</table>"

        # Footer
        html += '<div class="footer">'
        html += '<table style="border: none; width: 100%;"><tr>'
        html += f'<td style="border: none; text-align: left; width: 33%;">{self._footer_left.text()}</td>'
        footer_center = self._footer_center.text().replace("{page}", "1").replace("{pages}", "1")
        html += f'<td style="border: none; text-align: center; width: 34%;">{footer_center}</td>'
        html += f'<td style="border: none; text-align: right; width: 33%;">{self._footer_right.text()}</td>'
        html += '</tr></table>'
        html += '</div>'

        html += "</body></html>"
        return html

    def _render_item_row(self, item, options: dict, level: int) -> str:
        """Render een item rij"""
        html = ""
        report_type = options["report_type"]

        # Bij 'Alleen hoofdstukken' alleen chapters tonen
        if report_type == "Alleen hoofdstukken" and not item.is_chapter:
            return ""

        # Bij 'Samenvatting per hoofdstuk' alleen chapters met totalen
        if report_type == "Samenvatting per hoofdstuk" and not item.is_chapter:
            return ""

        row_class = "chapter-row" if item.is_chapter else ""
        indent = "&nbsp;" * (level * 4)

        html += f"<tr class='{row_class}'>"
        html += f"<td>{item.identification}</td>"

        if options["include_sfb"]:
            html += f"<td>{item.sfb_code or ''}</td>"

        html += f"<td>{indent}{item.name}</td>"

        if options["include_quantities"]:
            if item.is_leaf:
                html += f"<td>{item.unit_symbol}</td>"
                html += f"<td class='number'>{self._locale.toString(item.quantity, 'f', 2)}</td>"
            else:
                html += "<td></td><td></td>"

        if options["include_unit_prices"]:
            if item.is_leaf:
                html += f"<td class='number'>{self._format_currency(item.unit_price)}</td>"
            else:
                html += "<td></td>"

        html += f"<td class='number'>{self._format_currency(item.subtotal)}</td>"
        html += "</tr>"

        # Recursief children
        if report_type in ["Volledige begroting", "Gedetailleerd met specificaties"]:
            for child in item.children:
                html += self._render_item_row(child, options, level + 1)

        return html

    def _format_currency(self, value: float) -> str:
        """Formatteer als valuta"""
        return f"&euro; {self._locale.toString(value, 'f', 2)}"

    def _export_pdf(self):
        """Exporteer rapport naar PDF"""
        if not self._schedule:
            QMessageBox.warning(self, "Geen begroting", "Laad eerst een begroting.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Rapport Exporteren als PDF",
            f"{self._schedule.name}_rapport.pdf",
            "PDF Bestanden (*.pdf)"
        )

        if file_path:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(file_path)

            if self._landscape_radio.isChecked():
                printer.setPageOrientation(QPrinter.Landscape)
            else:
                printer.setPageOrientation(QPrinter.Portrait)

            # Genereer HTML en print naar PDF
            html = self._generate_report_html()
            self._preview.setHtml(html)
            self._preview.document().print_(printer)

            QMessageBox.information(
                self,
                "Export Voltooid",
                f"Rapport geexporteerd naar:\n{file_path}"
            )

    def _print_report(self):
        """Print het rapport"""
        if not self._schedule:
            QMessageBox.warning(self, "Geen begroting", "Laad eerst een begroting.")
            return

        printer = QPrinter(QPrinter.HighResolution)

        if self._landscape_radio.isChecked():
            printer.setPageOrientation(QPrinter.Landscape)
        else:
            printer.setPageOrientation(QPrinter.Portrait)

        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QPrintDialog.Accepted:
            html = self._generate_report_html()
            self._preview.setHtml(html)
            self._preview.document().print_(printer)

    def get_options(self) -> dict:
        """Haal de geselecteerde opties op"""
        return {
            "report_type": self._report_type.currentText(),
            "include_project": self._include_project.isChecked(),
            "include_surcharges": self._include_surcharges.isChecked(),
            "include_vat": self._include_vat.isChecked(),
            "include_quantities": self._include_quantities.isChecked(),
            "include_unit_prices": self._include_unit_prices.isChecked(),
            "include_sfb": self._include_sfb.isChecked(),
            "orientation": "landscape" if self._landscape_radio.isChecked() else "portrait",
            "header_left": self._header_left.text(),
            "header_center": self._header_center.text(),
            "header_right": self._header_right.text(),
            "footer_left": self._footer_left.text(),
            "footer_center": self._footer_center.text(),
            "footer_right": self._footer_right.text(),
        }
