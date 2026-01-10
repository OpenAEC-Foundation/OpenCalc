"""
Print Service - Afdrukken en PDF export van begrotingen
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox
from PySide6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from PySide6.QtGui import QTextDocument, QFont, QTextCursor, QPageLayout, QPageSize
from PySide6.QtCore import Qt, QMarginsF, QDate

from pathlib import Path
from typing import Optional
from datetime import date

from ..models import CostSchedule, CostItem


class PrintService:
    """Service voor het afdrukken en exporteren van begrotingen"""

    def __init__(self, schedule: CostSchedule):
        self.schedule = schedule

    def generate_html(self, include_details: bool = True) -> str:
        """
        Genereer HTML representatie van de begroting.

        Args:
            include_details: Inclusief alle details per post

        Returns:
            HTML string
        """
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 10pt;
            line-height: 1.4;
            color: #333;
            margin: 0;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #2962ff;
            padding-bottom: 20px;
        }}
        .header h1 {{
            color: #1e40af;
            margin: 0 0 10px 0;
            font-size: 24pt;
        }}
        .header .subtitle {{
            color: #666;
            font-size: 11pt;
        }}
        .meta-info {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
            font-size: 9pt;
            color: #666;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        th {{
            background-color: #2962ff;
            color: white;
            padding: 10px 8px;
            text-align: left;
            font-weight: 600;
        }}
        th.right, td.right {{
            text-align: right;
        }}
        td {{
            padding: 8px;
            border-bottom: 1px solid #e0e0e0;
        }}
        tr.chapter {{
            background-color: #e3f2fd;
            font-weight: 600;
        }}
        tr.chapter td {{
            border-bottom: 2px solid #2962ff;
            padding-top: 12px;
            padding-bottom: 12px;
        }}
        tr.item:hover {{
            background-color: #f5f5f5;
        }}
        tr.subtotal {{
            background-color: #fff3e0;
            font-weight: 600;
        }}
        .totals {{
            margin-top: 30px;
            border-top: 2px solid #2962ff;
            padding-top: 20px;
        }}
        .totals table {{
            width: 350px;
            margin-left: auto;
        }}
        .totals td {{
            padding: 8px 12px;
        }}
        .totals tr.grand-total {{
            background-color: #2962ff;
            color: white;
            font-weight: bold;
            font-size: 12pt;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            font-size: 8pt;
            color: #999;
            text-align: center;
        }}
        .page-break {{
            page-break-before: always;
        }}
        @media print {{
            body {{
                padding: 0;
            }}
            .no-print {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{self._escape_html(self.schedule.name)}</h1>
        <div class="subtitle">{self._escape_html(self.schedule.description or 'Kostenbegroting')}</div>
    </div>

    <div class="meta-info">
        <div>
            <strong>Datum:</strong> {date.today().strftime('%d-%m-%Y')}<br>
            <strong>Status:</strong> {self.schedule.status.value}
        </div>
        <div style="text-align: right;">
            <strong>Type:</strong> {self.schedule.schedule_type.value}<br>
            <strong>Aantal posten:</strong> {self.schedule.item_count}
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th style="width: 80px;">Code</th>
                <th>Omschrijving</th>
                <th class="right" style="width: 60px;">Eenh.</th>
                <th class="right" style="width: 80px;">Hoev.</th>
                <th class="right" style="width: 100px;">Prijs</th>
                <th class="right" style="width: 120px;">Totaal</th>
            </tr>
        </thead>
        <tbody>
"""

        # Genereer rijen voor elk hoofdstuk en item
        for chapter in self.schedule.items:
            html += self._generate_chapter_rows(chapter, include_details)

        html += f"""
        </tbody>
    </table>

    <div class="totals">
        <table>
            <tr>
                <td>Subtotaal excl. BTW</td>
                <td class="right">{self.schedule.format_subtotal()}</td>
            </tr>
            <tr>
                <td>BTW {self.schedule.vat_rate:.0f}%</td>
                <td class="right">{self.schedule.format_vat()}</td>
            </tr>
            <tr class="grand-total">
                <td>Totaal incl. BTW</td>
                <td class="right">{self.schedule.format_total()}</td>
            </tr>
        </table>
    </div>

    <div class="footer">
        <p>Gegenereerd met OpenCalc | {date.today().strftime('%d-%m-%Y %H:%M')}</p>
    </div>
</body>
</html>
"""
        return html

    def _generate_chapter_rows(self, chapter: CostItem, include_details: bool) -> str:
        """Genereer HTML rijen voor een hoofdstuk"""
        html = f"""
            <tr class="chapter">
                <td>{self._escape_html(chapter.identification)}</td>
                <td colspan="4">{self._escape_html(chapter.name)}</td>
                <td class="right">{chapter.format_subtotal()}</td>
            </tr>
"""

        if include_details:
            for item in chapter.children:
                if item.is_chapter:
                    # Sub-hoofdstuk
                    html += self._generate_chapter_rows(item, include_details)
                else:
                    # Kostenpost
                    html += f"""
            <tr class="item">
                <td style="padding-left: {20 + item.level * 15}px;">{self._escape_html(item.identification)}</td>
                <td>{self._escape_html(item.name)}</td>
                <td class="right">{item.unit_symbol}</td>
                <td class="right">{item.quantity:,.2f}</td>
                <td class="right">€ {item.unit_price:,.2f}</td>
                <td class="right">{item.format_subtotal()}</td>
            </tr>
"""

        return html

    def _escape_html(self, text: str) -> str:
        """Escape HTML speciale tekens"""
        if not text:
            return ""
        return (text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;"))

    def print_preview(self, parent=None) -> bool:
        """
        Toon print preview dialoog.

        Args:
            parent: Parent widget

        Returns:
            True als er geprint werd
        """
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QPageSize(QPageSize.A4))
        printer.setPageOrientation(QPageLayout.Portrait)

        preview = QPrintPreviewDialog(printer, parent)
        preview.setWindowTitle(f"Afdrukvoorbeeld - {self.schedule.name}")
        preview.paintRequested.connect(lambda p: self._render_to_printer(p))
        preview.resize(900, 700)

        result = preview.exec()
        return result == QDialog.Accepted

    def print_direct(self, parent=None) -> bool:
        """
        Toon print dialoog en print direct.

        Args:
            parent: Parent widget

        Returns:
            True als er geprint werd
        """
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QPageSize(QPageSize.A4))

        dialog = QPrintDialog(printer, parent)
        dialog.setWindowTitle("Afdrukken")

        if dialog.exec() == QDialog.Accepted:
            self._render_to_printer(printer)
            return True
        return False

    def _render_to_printer(self, printer: QPrinter):
        """Render de begroting naar de printer"""
        document = QTextDocument()
        document.setHtml(self.generate_html())
        document.setPageSize(printer.pageRect(QPrinter.Point).size())
        document.print_(printer)

    def export_pdf(self, file_path: str) -> bool:
        """
        Exporteer de begroting naar PDF.

        Args:
            file_path: Pad naar het PDF bestand

        Returns:
            True als succesvol
        """
        try:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(file_path)
            printer.setPageSize(QPageSize(QPageSize.A4))
            printer.setPageOrientation(QPageLayout.Portrait)

            # Marges instellen
            margins = QMarginsF(15, 15, 15, 15)  # mm
            printer.setPageMargins(margins, QPageLayout.Millimeter)

            self._render_to_printer(printer)
            return True
        except Exception as e:
            print(f"Fout bij PDF export: {e}")
            return False

    def export_html(self, file_path: str) -> bool:
        """
        Exporteer de begroting naar HTML.

        Args:
            file_path: Pad naar het HTML bestand

        Returns:
            True als succesvol
        """
        try:
            html = self.generate_html()
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html)
            return True
        except Exception as e:
            print(f"Fout bij HTML export: {e}")
            return False


class PrintPreviewDialog(QDialog):
    """Aangepaste print preview dialoog met extra opties"""

    def __init__(self, schedule: CostSchedule, parent=None):
        super().__init__(parent)
        self.schedule = schedule
        self.print_service = PrintService(schedule)

        self.setWindowTitle(f"Afdrukvoorbeeld - {schedule.name}")
        self.resize(900, 700)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Preview tekst
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setHtml(self.print_service.generate_html())
        layout.addWidget(self.preview)

        # Knoppen
        buttons = QDialogButtonBox()

        self.print_btn = buttons.addButton("Afdrukken", QDialogButtonBox.ActionRole)
        self.print_btn.clicked.connect(self._on_print)

        self.pdf_btn = buttons.addButton("Exporteer PDF", QDialogButtonBox.ActionRole)
        self.pdf_btn.clicked.connect(self._on_export_pdf)

        buttons.addButton(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

    def _on_print(self):
        if self.print_service.print_direct(self):
            self.accept()

    def _on_export_pdf(self):
        from PySide6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "PDF Exporteren",
            f"{self.schedule.name}.pdf",
            "PDF Bestanden (*.pdf)"
        )

        if file_path:
            if self.print_service.export_pdf(file_path):
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(
                    self,
                    "Export Succesvol",
                    f"PDF opgeslagen als:\n{file_path}"
                )
