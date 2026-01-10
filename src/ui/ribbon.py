"""
Ribbon Toolbar - Moderne Office-stijl ribbon interface
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QToolButton,
    QFrame, QLabel, QSizePolicy, QGridLayout, QButtonGroup, QColorDialog
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QAction, QColor

from .icons import IconProvider


class RibbonButton(QToolButton):
    """Grote ribbon knop met icoon en tekst"""

    def __init__(self, text: str, icon_name: str = None, parent=None):
        super().__init__(parent)
        self.setText(text)
        if icon_name:
            self.setIcon(IconProvider.get_icon(icon_name, 32))
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setIconSize(QSize(32, 32))
        self.setMinimumWidth(60)
        self.setMaximumWidth(80)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setStyleSheet("""
            QToolButton {
                border: 1px solid transparent;
                border-radius: 6px;
                padding: 6px 4px;
                background: transparent;
                font-size: 9pt;
                color: #1e293b;
            }
            QToolButton:hover {
                background-color: #e0f2fe;
                border: 1px solid #7dd3fc;
            }
            QToolButton:pressed {
                background-color: #bae6fd;
            }
            QToolButton:checked {
                background-color: #bae6fd;
                border: 1px solid #0ea5e9;
            }
        """)


class RibbonSmallButton(QToolButton):
    """Kleine ribbon knop voor secundaire acties"""

    def __init__(self, text: str, icon_name: str = None, parent=None):
        super().__init__(parent)
        self.setText(text)
        if icon_name:
            self.setIcon(IconProvider.get_icon(icon_name, 16))
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.setIconSize(QSize(16, 16))
        self.setStyleSheet("""
            QToolButton {
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 3px 8px;
                background: transparent;
                font-size: 9pt;
                text-align: left;
                color: #1e293b;
            }
            QToolButton:hover {
                background-color: #e0f2fe;
                border: 1px solid #7dd3fc;
            }
            QToolButton:pressed {
                background-color: #bae6fd;
            }
        """)


class RibbonSeparator(QFrame):
    """Verticale scheiding tussen ribbon groepen"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Plain)
        self.setStyleSheet("color: #e2e8f0;")


class RibbonGroup(QFrame):
    """Groep van gerelateerde knoppen in de ribbon"""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.NoFrame)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 2)
        layout.setSpacing(2)

        # Content area
        self._content = QWidget()
        self._content_layout = QHBoxLayout(self._content)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(2)
        layout.addWidget(self._content, 1)

        # Title label
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 8pt;
            color: #64748b;
            padding: 2px;
            border-top: 1px solid #e2e8f0;
        """)
        layout.addWidget(title_label)

    def add_button(self, button: QToolButton):
        """Voeg een knop toe aan de groep"""
        self._content_layout.addWidget(button)

    def add_widget(self, widget: QWidget):
        """Voeg een widget toe aan de groep"""
        self._content_layout.addWidget(widget)

    def add_small_button_column(self, buttons: list):
        """Voeg een kolom met kleine knoppen toe"""
        column = QWidget()
        col_layout = QVBoxLayout(column)
        col_layout.setContentsMargins(0, 0, 0, 0)
        col_layout.setSpacing(1)
        for btn in buttons:
            col_layout.addWidget(btn)
        self._content_layout.addWidget(column)


class RibbonTab(QWidget):
    """Een tab in de ribbon met groepen"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(4, 4, 4, 4)
        self._layout.setSpacing(8)
        self._layout.addStretch()

    def add_group(self, group: RibbonGroup):
        """Voeg een groep toe aan de tab"""
        self._layout.insertWidget(self._layout.count() - 1, group)

    def add_separator(self):
        """Voeg een scheiding toe"""
        sep = RibbonSeparator()
        self._layout.insertWidget(self._layout.count() - 1, sep)


class Ribbon(QWidget):
    """Office-stijl Ribbon toolbar"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumHeight(140)
        self.setMaximumHeight(150)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Tab widget
        self._tabs = QTabWidget()
        self._tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8fafc, stop:1 #f1f5f9);
                border-bottom: 1px solid #e2e8f0;
            }
            QTabBar::tab {
                background: transparent;
                border: none;
                padding: 8px 16px;
                margin-right: 2px;
                font-weight: 500;
                color: #475569;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8fafc, stop:1 #f1f5f9);
                border-top: 3px solid #0ea5e9;
                border-left: 1px solid #e2e8f0;
                border-right: 1px solid #e2e8f0;
                color: #0ea5e9;
            }
            QTabBar::tab:hover:!selected {
                background: #f1f5f9;
            }
        """)
        layout.addWidget(self._tabs)

    def add_tab(self, tab: RibbonTab, title: str) -> int:
        """Voeg een tab toe aan de ribbon"""
        return self._tabs.addTab(tab, title)

    def current_tab(self) -> RibbonTab:
        """Geef de huidige tab terug"""
        return self._tabs.currentWidget()

    def set_current_tab(self, index: int):
        """Selecteer een tab"""
        self._tabs.setCurrentIndex(index)


class OpenCalcRibbon(Ribbon):
    """OpenCalc specifieke ribbon met alle tabs en acties"""

    # Signals voor acties
    newFile = Signal()
    openFile = Signal()
    saveFile = Signal()
    saveFileAs = Signal()
    printPreview = Signal()
    printFile = Signal()
    exportPdf = Signal()
    exportHtml = Signal()
    exportXls = Signal()
    exportOds = Signal()

    # Import signals
    importExcel = Signal()
    importCsv = Signal()

    # Undo/Redo signals
    undoAction = Signal()
    redoAction = Signal()

    # Clipboard signals
    cutItem = Signal()
    copyItem = Signal()
    pasteItem = Signal()

    addChapter = Signal()
    addCostItem = Signal()
    addTextRow = Signal()  # Tekstregel zonder kosten
    deleteItem = Signal()

    # Regel signals
    moveUp = Signal()
    moveDown = Signal()
    indentIn = Signal()
    indentOut = Signal()

    # Document signals
    openPdf = Signal()
    openIfc = Signal()
    openIfc3D = Signal()
    openDxf = Signal()

    # Import signals (nieuw)
    importPdf = Signal()
    importIfc = Signal()
    importDwg = Signal()

    toggleDarkMode = Signal(bool)

    # Text formatting signals
    formatBold = Signal(bool)
    formatItalic = Signal(bool)
    formatUnderline = Signal(bool)
    formatColor = Signal(object)  # QColor

    # Export signals
    exportOds = Signal()
    exportOdt = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._setup_home_tab()
        self._setup_import_tab()
        self._setup_view_tab()

    def _setup_home_tab(self):
        """Configureer de Start tab (alles gecombineerd)"""
        tab = RibbonTab()

        # Bestand groep
        file_group = RibbonGroup("Bestand")

        self._new_btn = RibbonButton("Nieuw", "new")
        self._new_btn.clicked.connect(self.newFile.emit)
        file_group.add_button(self._new_btn)

        self._open_btn = RibbonButton("Openen", "open")
        self._open_btn.clicked.connect(self.openFile.emit)
        file_group.add_button(self._open_btn)

        self._save_btn = RibbonButton("Opslaan", "save")
        self._save_btn.clicked.connect(self.saveFile.emit)
        file_group.add_button(self._save_btn)

        tab.add_group(file_group)
        tab.add_separator()

        # Ongedaan maken groep
        undo_group = RibbonGroup("Ongedaan maken")

        self._undo_btn = RibbonButton("Ongedaan\nmaken", "undo")
        self._undo_btn.setToolTip("Ongedaan maken (Ctrl+Z)")
        self._undo_btn.clicked.connect(self.undoAction.emit)
        undo_group.add_button(self._undo_btn)

        self._redo_btn = RibbonButton("Opnieuw", "redo")
        self._redo_btn.setToolTip("Opnieuw (Ctrl+Y)")
        self._redo_btn.clicked.connect(self.redoAction.emit)
        undo_group.add_button(self._redo_btn)

        tab.add_group(undo_group)
        tab.add_separator()

        # Structuur groep
        structure_group = RibbonGroup("Invoegen")

        self._add_chapter_btn = RibbonButton("Hoofdstuk", "chapter")
        self._add_chapter_btn.clicked.connect(self.addChapter.emit)
        structure_group.add_button(self._add_chapter_btn)

        self._add_item_btn = RibbonButton("Kostenpost", "cost_item")
        self._add_item_btn.clicked.connect(self.addCostItem.emit)
        structure_group.add_button(self._add_item_btn)

        self._add_text_btn = RibbonButton("Tekstregel", "text_row")
        self._add_text_btn.setToolTip("Voeg tekstregel toe zonder kosten")
        self._add_text_btn.clicked.connect(self.addTextRow.emit)
        structure_group.add_button(self._add_text_btn)

        self._delete_btn = RibbonButton("Verwijderen", "delete")
        self._delete_btn.clicked.connect(self.deleteItem.emit)
        structure_group.add_button(self._delete_btn)

        tab.add_group(structure_group)
        tab.add_separator()

        # Import groep
        import_group = RibbonGroup("Importeren")

        import_excel_btn = RibbonSmallButton("Excel Import", "excel")
        import_excel_btn.clicked.connect(self.importExcel.emit)

        import_csv_btn = RibbonSmallButton("CSV Import", "csv")
        import_csv_btn.clicked.connect(self.importCsv.emit)

        import_group.add_small_button_column([import_excel_btn, import_csv_btn])

        tab.add_group(import_group)
        tab.add_separator()

        # Bewerken groep (klembord)
        edit_group = RibbonGroup("Bewerken")

        self._cut_btn = RibbonButton("Knippen", "cut")
        self._cut_btn.clicked.connect(self.cutItem.emit)
        edit_group.add_button(self._cut_btn)

        self._copy_btn = RibbonButton("Kopiëren", "copy")
        self._copy_btn.clicked.connect(self.copyItem.emit)
        edit_group.add_button(self._copy_btn)

        self._paste_btn = RibbonButton("Plakken", "paste")
        self._paste_btn.clicked.connect(self.pasteItem.emit)
        edit_group.add_button(self._paste_btn)

        tab.add_group(edit_group)
        tab.add_separator()

        # Opmaak groep
        format_group = RibbonGroup("Opmaak")

        self._bold_btn = RibbonSmallButton("B", "bold")
        self._bold_btn.setCheckable(True)
        self._bold_btn.setToolTip("Vet (Ctrl+B)")
        self._bold_btn.setStyleSheet("""
            QToolButton {
                font-weight: bold;
                font-size: 11pt;
                min-width: 28px;
                max-width: 28px;
            }
        """)
        self._bold_btn.toggled.connect(self.formatBold.emit)

        self._italic_btn = RibbonSmallButton("I", "italic")
        self._italic_btn.setCheckable(True)
        self._italic_btn.setToolTip("Cursief (Ctrl+I)")
        self._italic_btn.setStyleSheet("""
            QToolButton {
                font-style: italic;
                font-size: 11pt;
                min-width: 28px;
                max-width: 28px;
            }
        """)
        self._italic_btn.toggled.connect(self.formatItalic.emit)

        self._underline_btn = RibbonSmallButton("U", "underline")
        self._underline_btn.setCheckable(True)
        self._underline_btn.setToolTip("Onderstrepen (Ctrl+U)")
        self._underline_btn.setStyleSheet("""
            QToolButton {
                text-decoration: underline;
                font-size: 11pt;
                min-width: 28px;
                max-width: 28px;
            }
        """)
        self._underline_btn.toggled.connect(self.formatUnderline.emit)

        self._color_btn = RibbonSmallButton("A", "color")
        self._color_btn.setToolTip("Tekstkleur")
        self._color_btn.setStyleSheet("""
            QToolButton {
                font-size: 11pt;
                font-weight: bold;
                min-width: 28px;
                max-width: 28px;
                border-bottom: 3px solid #e74c3c;
            }
        """)
        self._color_btn.clicked.connect(self._choose_color)
        self._current_color = QColor("#000000")

        format_group.add_small_button_column([self._bold_btn, self._italic_btn])
        format_group.add_small_button_column([self._underline_btn, self._color_btn])

        tab.add_group(format_group)
        tab.add_separator()

        # Export groep
        export_group = RibbonGroup("Exporteren")

        self._print_btn = RibbonButton("Afdrukken", "print")
        self._print_btn.clicked.connect(self.printFile.emit)
        export_group.add_button(self._print_btn)

        # Export knoppen als kolom
        pdf_btn = RibbonSmallButton("PDF Export", "pdf")
        pdf_btn.clicked.connect(self.exportPdf.emit)

        xls_btn = RibbonSmallButton("Excel Export", "excel")
        xls_btn.clicked.connect(self.exportXls.emit)

        ods_btn = RibbonSmallButton("ODS Export", "ods")
        ods_btn.clicked.connect(self.exportOds.emit)

        odt_btn = RibbonSmallButton("ODT Export", "odt")
        odt_btn.clicked.connect(self.exportOdt.emit)

        export_group.add_small_button_column([pdf_btn, xls_btn])
        export_group.add_small_button_column([ods_btn, odt_btn])

        tab.add_group(export_group)

        self.add_tab(tab, "Start")

    def _setup_import_tab(self):
        """Configureer de Import tab"""
        tab = RibbonTab()

        # Documenten import groep
        docs_group = RibbonGroup("Documenten Importeren")

        self._import_pdf_btn = RibbonButton("PDF", "pdf")
        self._import_pdf_btn.setToolTip("PDF document importeren voor referentie")
        self._import_pdf_btn.clicked.connect(self.importPdf.emit)
        docs_group.add_button(self._import_pdf_btn)

        self._import_ifc_btn = RibbonButton("IFC", "ifc")
        self._import_ifc_btn.setToolTip("IFC model importeren (bouwkundig model)")
        self._import_ifc_btn.clicked.connect(self.importIfc.emit)
        docs_group.add_button(self._import_ifc_btn)

        self._import_dwg_btn = RibbonButton("DWG/DXF", "dxf")
        self._import_dwg_btn.setToolTip("AutoCAD DWG/DXF tekening importeren")
        self._import_dwg_btn.clicked.connect(self.importDwg.emit)
        docs_group.add_button(self._import_dwg_btn)

        tab.add_group(docs_group)
        tab.add_separator()

        # Data import groep
        data_group = RibbonGroup("Data Importeren")

        import_excel_btn = RibbonButton("Excel", "excel")
        import_excel_btn.setToolTip("Excel bestand importeren")
        import_excel_btn.clicked.connect(self.importExcel.emit)
        data_group.add_button(import_excel_btn)

        import_csv_btn = RibbonButton("CSV", "csv")
        import_csv_btn.setToolTip("CSV bestand importeren")
        import_csv_btn.clicked.connect(self.importCsv.emit)
        data_group.add_button(import_csv_btn)

        tab.add_group(data_group)

        self.add_tab(tab, "Import")

    def _setup_view_tab(self):
        """Configureer de Weergave tab"""
        tab = RibbonTab()

        # Panelen groep
        panels_group = RibbonGroup("Panelen")

        self._toggle_props_btn = RibbonButton("Eigenschappen")
        self._toggle_props_btn.setCheckable(True)
        self._toggle_props_btn.setChecked(False)
        panels_group.add_button(self._toggle_props_btn)

        self._toggle_docs_btn = RibbonButton("Documenten")
        self._toggle_docs_btn.setCheckable(True)
        self._toggle_docs_btn.setChecked(False)
        panels_group.add_button(self._toggle_docs_btn)

        tab.add_group(panels_group)
        tab.add_separator()

        # Zoom groep
        zoom_group = RibbonGroup("Zoom")

        self._zoom_in_btn = RibbonButton("Inzoomen", "zoom_in")
        zoom_group.add_button(self._zoom_in_btn)

        self._zoom_out_btn = RibbonButton("Uitzoomen", "zoom_out")
        zoom_group.add_button(self._zoom_out_btn)

        self._zoom_fit_btn = RibbonButton("Passend", "fit")
        zoom_group.add_button(self._zoom_fit_btn)

        tab.add_group(zoom_group)
        tab.add_separator()

        # Thema groep
        theme_group = RibbonGroup("Thema")

        self._dark_mode_btn = RibbonButton("Dark Mode")
        self._dark_mode_btn.setCheckable(True)
        self._dark_mode_btn.setChecked(False)
        self._dark_mode_btn.toggled.connect(self.toggleDarkMode.emit)
        theme_group.add_button(self._dark_mode_btn)

        tab.add_group(theme_group)

        self.add_tab(tab, "Weergave")

    def _choose_color(self):
        """Open kleurkiezer dialoog"""
        color = QColorDialog.getColor(self._current_color, self, "Kies tekstkleur")
        if color.isValid():
            self._current_color = color
            # Update knop kleur indicator
            self._color_btn.setStyleSheet(f"""
                QToolButton {{
                    font-size: 11pt;
                    font-weight: bold;
                    min-width: 28px;
                    max-width: 28px;
                    border-bottom: 3px solid {color.name()};
                }}
            """)
            self.formatColor.emit(color)
