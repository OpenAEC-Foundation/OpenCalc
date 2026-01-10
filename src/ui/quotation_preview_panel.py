"""
QuotationPreviewPanel - Paneel voor offerte preview
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolBar, QLabel,
    QPushButton, QFrame, QScrollArea, QTextBrowser
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtPrintSupport import QPrinter, QPrintDialog

# Probeer WebEngine te importeren, val terug op QTextBrowser
try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False


class QuotationPreviewPanel(QWidget):
    """Paneel voor het bekijken en afdrukken van offertes"""

    printQuotation = Signal()
    exportPdf = Signal()
    exportWord = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Stel de UI in"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background: #f1f5f9;
                border-bottom: 1px solid #e2e8f0;
                padding: 4px;
                spacing: 8px;
            }
        """)

        # Print knop
        print_btn = QPushButton("Afdrukken")
        print_btn.setStyleSheet("""
            QPushButton {
                background-color: #0ea5e9;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #0284c7;
            }
        """)
        print_btn.clicked.connect(self.printQuotation.emit)
        toolbar.addWidget(print_btn)

        toolbar.addSeparator()

        # Export PDF knop
        pdf_btn = QPushButton("PDF Exporteren")
        pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        pdf_btn.clicked.connect(self.exportPdf.emit)
        toolbar.addWidget(pdf_btn)

        # Export Word knop
        word_btn = QPushButton("Word Exporteren")
        word_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        word_btn.clicked.connect(self.exportWord.emit)
        toolbar.addWidget(word_btn)

        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(spacer.sizePolicy().horizontalPolicy(),
                            spacer.sizePolicy().verticalPolicy())
        spacer.setMinimumWidth(0)
        toolbar.addWidget(spacer)

        # Zoom controls
        toolbar.addWidget(QLabel("Zoom:"))

        zoom_out_btn = QPushButton("-")
        zoom_out_btn.setFixedWidth(30)
        zoom_out_btn.clicked.connect(self._zoom_out)
        toolbar.addWidget(zoom_out_btn)

        self._zoom_label = QLabel("100%")
        self._zoom_label.setMinimumWidth(50)
        self._zoom_label.setAlignment(Qt.AlignCenter)
        toolbar.addWidget(self._zoom_label)

        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setFixedWidth(30)
        zoom_in_btn.clicked.connect(self._zoom_in)
        toolbar.addWidget(zoom_in_btn)

        layout.addWidget(toolbar)

        # Preview container met padding
        preview_container = QFrame()
        preview_container.setStyleSheet("""
            QFrame {
                background-color: #64748b;
            }
        """)
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(40, 20, 40, 20)

        # Web view of text browser voor HTML preview
        self._zoom_factor = 1.0

        if HAS_WEBENGINE:
            self._web_view = QWebEngineView()
            self._web_view.setStyleSheet("QWebEngineView { background: white; }")
            self._use_webengine = True
        else:
            # Fallback naar QTextBrowser
            self._web_view = QTextBrowser()
            self._web_view.setOpenExternalLinks(True)
            self._web_view.setStyleSheet("QTextBrowser { background: white; }")
            self._use_webengine = False

        # Start met placeholder content
        self._set_placeholder_content()

        preview_layout.addWidget(self._web_view)

        layout.addWidget(preview_container, 1)

    def _set_placeholder_content(self):
        """Stel placeholder content in"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    margin: 40px;
                    color: #334155;
                }
                .placeholder {
                    text-align: center;
                    padding: 100px;
                    color: #94a3b8;
                }
                .placeholder h2 {
                    color: #64748b;
                    margin-bottom: 20px;
                }
            </style>
        </head>
        <body>
            <div class="placeholder">
                <h2>Offerte Preview</h2>
                <p>Genereer eerst een offerte via het "Offerte" tabblad.</p>
                <p>De offerte wordt hier weergegeven als PDF-achtig document.</p>
            </div>
        </body>
        </html>
        """
        self._web_view.setHtml(html)

    def set_content(self, html: str):
        """Stel de offerte content in"""
        self._web_view.setHtml(html)

    def _zoom_in(self):
        """Zoom in"""
        if self._zoom_factor < 2.0:
            self._zoom_factor += 0.1
            if self._use_webengine:
                self._web_view.setZoomFactor(self._zoom_factor)
            self._zoom_label.setText(f"{int(self._zoom_factor * 100)}%")

    def _zoom_out(self):
        """Zoom out"""
        if self._zoom_factor > 0.5:
            self._zoom_factor -= 0.1
            if self._use_webengine:
                self._web_view.setZoomFactor(self._zoom_factor)
            self._zoom_label.setText(f"{int(self._zoom_factor * 100)}%")

    def print_quotation(self):
        """Print de offerte"""
        self.printQuotation.emit()

    def get_web_view(self) -> QWebEngineView:
        """Geef de web view terug voor printing"""
        return self._web_view
