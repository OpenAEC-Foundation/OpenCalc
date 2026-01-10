"""
MainWindow - Hoofdvenster van de OpenCalc applicatie
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QMenuBar, QMenu, QToolBar, QStatusBar, QFileDialog, QMessageBox,
    QLabel, QFrame, QTabWidget, QDockWidget, QApplication
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QKeySequence, QClipboard

from pathlib import Path
from typing import Optional

from ..models import CostSchedule, CostItem
from ..ifc import IFCHandler, CostAPI
from .cost_table import CostTableView
from .properties_panel import PropertiesPanel
from .ribbon import OpenCalcRibbon
from .document_viewer import DocumentViewerPanel
from .ifc_3d_viewer import IFC3DViewerPanel
from .surcharges_panel import SurchargesPanel
from .project_panel import ProjectPanel
from .report_panel import ReportPanel
from .quotation_panel import QuotationPanel


class MainWindow(QMainWindow):
    """Hoofdvenster van de OpenCalc applicatie"""

    scheduleChanged = Signal(object)  # CostSchedule
    selectionChanged = Signal(object)  # CostItem

    def __init__(self, initial_file: Optional[str] = None):
        super().__init__()

        self._ifc_handler = IFCHandler()
        self._cost_api: Optional[CostAPI] = None
        self._schedule: Optional[CostSchedule] = None

        # Undo/Redo stacks
        self._undo_stack = []
        self._redo_stack = []
        self._max_undo_levels = 50

        self._setup_ui()
        self._setup_menu()
        self._setup_statusbar()
        self._connect_signals()

        # Open initieel bestand of STABU voorbeeldbegroting
        if initial_file and Path(initial_file).exists():
            self._open_file_path(initial_file)
        else:
            # Probeer de STABU voorbeeldbegroting te openen
            stabu_example = Path(__file__).parent.parent.parent / "voorbeelden" / "woning_stabu_begroting.ifc"
            if stabu_example.exists():
                self._open_file_path(str(stabu_example))
            else:
                self._new_file()

    def _setup_ui(self):
        """Stel de UI componenten in"""
        self.setWindowTitle("OpenCalc")
        self.setMinimumSize(800, 600)
        self.resize(1600, 1000)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Ribbon toolbar
        self._ribbon = OpenCalcRibbon()
        main_layout.addWidget(self._ribbon)

        # Content area met splitters
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Hoofd horizontale splitter (documenten | begroting)
        self._main_splitter = QSplitter(Qt.Horizontal)

        # Document viewer paneel (links, initieel verborgen)
        self._doc_viewer = DocumentViewerPanel()
        self._doc_viewer.hide()  # Start verborgen zodat begroting focus heeft
        self._main_splitter.addWidget(self._doc_viewer)

        # Begroting paneel met document tabs bovenin
        budget_container = QWidget()
        budget_container_layout = QVBoxLayout(budget_container)
        budget_container_layout.setContentsMargins(0, 0, 0, 0)
        budget_container_layout.setSpacing(0)

        # Document tabs bovenin voor meerdere begrotingen
        self._document_tabs = QTabWidget()
        self._document_tabs.setTabsClosable(True)
        self._document_tabs.setMovable(True)
        self._document_tabs.tabCloseRequested.connect(self._close_document_tab)
        self._document_tabs.currentChanged.connect(self._on_document_tab_changed)
        self._document_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: white;
            }
            QTabBar::tab {
                background: #e2e8f0;
                border: 1px solid #cbd5e1;
                border-bottom: none;
                padding: 6px 16px;
                margin-right: 2px;
                font-size: 9pt;
            }
            QTabBar::tab:selected {
                background: white;
                border-top: 2px solid #0ea5e9;
            }
            QTabBar::tab:hover:!selected {
                background: #f1f5f9;
            }
            QTabBar::close-button {
                image: url(close.png);
                subcontrol-position: right;
            }
        """)

        # Eerste document tab (wordt gevuld bij openen)
        self._create_document_tab()

        budget_container_layout.addWidget(self._document_tabs)
        self._main_splitter.addWidget(budget_container)

        # Stel verhoudingen in
        self._main_splitter.setStretchFactor(0, 1)  # Documenten
        self._main_splitter.setStretchFactor(1, 3)  # Begroting
        self._main_splitter.setSizes([400, 1200])

        content_layout.addWidget(self._main_splitter)

        main_layout.addWidget(content)

        # Properties dock widget (links of rechts)
        self._properties_dock = QDockWidget("Eigenschappen", self)
        self._properties_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self._properties_panel = PropertiesPanel()
        self._properties_dock.setWidget(self._properties_panel)
        self._properties_dock.setMinimumWidth(300)
        self.addDockWidget(Qt.RightDockWidgetArea, self._properties_dock)
        self._properties_dock.hide()  # Start verborgen

        # Clipboard voor kopiëren/plakken
        self._clipboard_item: Optional[CostItem] = None

    def _create_document_tab(self, name: str = "Nieuwe Begroting") -> QWidget:
        """Maak een nieuwe document tab met alle subtabs"""
        doc_widget = QWidget()
        doc_layout = QVBoxLayout(doc_widget)
        doc_layout.setContentsMargins(0, 0, 0, 0)
        doc_layout.setSpacing(0)

        # Subtabs voor alle onderdelen
        sub_tabs = QTabWidget()
        sub_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: white;
            }
            QTabBar::tab {
                background: #f1f5f9;
                border: 1px solid #cbd5e1;
                border-bottom: none;
                padding: 8px 20px;
                margin-right: 2px;
                font-weight: 500;
                font-size: 10pt;
            }
            QTabBar::tab:selected {
                background: white;
                border-top: 3px solid #0ea5e9;
            }
            QTabBar::tab:hover:!selected {
                background: #e2e8f0;
            }
        """)

        # Tab 1: Projectgegevens
        project_panel = ProjectPanel()
        sub_tabs.addTab(project_panel, "Projectgegevens")

        # Tab 2: Begroting (tabel)
        budget_tab = QWidget()
        budget_tab_layout = QVBoxLayout(budget_tab)
        budget_tab_layout.setContentsMargins(0, 0, 0, 0)
        budget_tab_layout.setSpacing(0)

        table_view = CostTableView()
        budget_tab_layout.addWidget(table_view)

        sub_tabs.addTab(budget_tab, "Begroting")

        # Tab 3: Opslagen
        surcharges_panel = SurchargesPanel()
        sub_tabs.addTab(surcharges_panel, "Opslagen")

        # Tab 4: Rapport
        report_panel = ReportPanel()
        sub_tabs.addTab(report_panel, "Rapport")

        # Tab 5: Offerte (inclusief preview)
        quotation_panel = QuotationPanel()
        sub_tabs.addTab(quotation_panel, "Offerte")

        # Start op de Begroting tab (index 1)
        sub_tabs.setCurrentIndex(1)

        doc_layout.addWidget(sub_tabs)

        # Sla referenties op in het widget
        doc_widget.table_view = table_view
        doc_widget.project_panel = project_panel
        doc_widget.surcharges_panel = surcharges_panel
        doc_widget.report_panel = report_panel
        doc_widget.quotation_panel = quotation_panel
        doc_widget.sub_tabs = sub_tabs
        doc_widget.schedule = None
        doc_widget.file_path = None

        # Voeg tab toe
        tab_index = self._document_tabs.addTab(doc_widget, name)
        self._document_tabs.setCurrentIndex(tab_index)

        return doc_widget

    def _close_document_tab(self, index: int):
        """Sluit een document tab"""
        if self._document_tabs.count() <= 1:
            # Minstens 1 tab openhouden
            return

        doc_widget = self._document_tabs.widget(index)
        # Controleer of opgeslagen moet worden
        if doc_widget.schedule and self._ifc_handler.is_modified:
            reply = QMessageBox.question(
                self,
                "Document sluiten",
                "Wilt u de wijzigingen opslaan voordat u sluit?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Save:
                self._save_file()

        self._document_tabs.removeTab(index)

    def _on_document_tab_changed(self, index: int):
        """Afhandeling van tab wissel"""
        if index < 0:
            return

        doc_widget = self._document_tabs.widget(index)
        if doc_widget and hasattr(doc_widget, 'schedule'):
            self._schedule = doc_widget.schedule
            self._table_view = doc_widget.table_view
            self._surcharges_panel = doc_widget.surcharges_panel
            self._update_title()

    @property
    def _current_doc_widget(self):
        """Geef het huidige document widget"""
        return self._document_tabs.currentWidget()

    # Clipboard operaties
    def _cut_item(self):
        """Knip het geselecteerde item"""
        item = self._table_view.get_selected_item()
        if item:
            self._clipboard_item = item
            # Verwijder item
            if item.parent:
                item.parent.remove_child(item)
            elif self._schedule:
                self._schedule.remove_item(item)
            self._ifc_handler.mark_modified()
            self._table_view.refresh()
            self._update_title()
            self._update_totals()
            self._statusbar.showMessage("Item geknipt")

    def _copy_item(self):
        """Kopieer het geselecteerde item"""
        item = self._table_view.get_selected_item()
        if item:
            # Maak een kopie van het item
            self._clipboard_item = item.copy()
            self._statusbar.showMessage("Item gekopieerd")

    def _paste_item(self):
        """Plak het gekopieerde item"""
        if not self._clipboard_item or not self._schedule:
            return

        # Bepaal parent
        selected = self._table_view.get_selected_item()
        if selected and selected.is_chapter:
            parent = selected
        elif selected and selected.parent:
            parent = selected.parent
        elif self._schedule.items:
            parent = self._schedule.items[0]
        else:
            self._statusbar.showMessage("Geen geldig doel voor plakken")
            return

        # Maak kopie en voeg toe
        new_item = self._clipboard_item.copy()
        new_item.identification = f"{len(parent.children) + 1:02d}"
        parent.add_child(new_item)

        # Maak IFC item
        if self._cost_api and parent.ifc_cost_item:
            ifc_item = self._cost_api.add_cost_item(
                cost_item=parent.ifc_cost_item,
                name=new_item.name,
                identification=new_item.identification
            )
            new_item.ifc_cost_item = ifc_item

        self._ifc_handler.mark_modified()
        self._table_view.refresh()
        self._update_title()
        self._update_totals()
        self._statusbar.showMessage("Item geplakt")

    # Tekst opmaak operaties
    def _toggle_bold(self, checked: bool):
        """Toggle vet tekst voor het geselecteerde item"""
        item = self._table_view.get_selected_item()
        if not item:
            return
        self._apply_html_format(item, "b", checked)

    def _toggle_italic(self, checked: bool):
        """Toggle schuin tekst voor het geselecteerde item"""
        item = self._table_view.get_selected_item()
        if not item:
            return
        self._apply_html_format(item, "i", checked)

    def _toggle_underline(self, checked: bool):
        """Toggle onderstreept tekst voor het geselecteerde item"""
        item = self._table_view.get_selected_item()
        if not item:
            return
        self._apply_html_format(item, "u", checked)

    def _set_text_color(self, color):
        """Stel tekstkleur in voor het geselecteerde item"""
        item = self._table_view.get_selected_item()
        if not item or not color.isValid():
            return

        # Verwijder bestaande kleur span en voeg nieuwe toe
        html = item.html_name or item.name
        import re
        # Verwijder bestaande color span
        html = re.sub(r'<span style="color:[^"]*">(.*?)</span>', r'\1', html)
        # Voeg nieuwe kleur toe
        color_hex = color.name()
        item.html_name = f'<span style="color:{color_hex}">{html}</span>'

        self._on_item_changed(item)
        self._table_view.refresh()
        self._statusbar.showMessage(f"Tekstkleur ingesteld: {color_hex}")

    def _apply_html_format(self, item: CostItem, tag: str, apply: bool):
        """Pas HTML opmaak toe op een item"""
        import re

        # Gebruik html_name als die bestaat, anders de naam
        html = item.html_name or item.name

        if apply:
            # Voeg tag toe als die nog niet bestaat
            if f"<{tag}>" not in html:
                html = f"<{tag}>{html}</{tag}>"
        else:
            # Verwijder de tag
            html = re.sub(f'<{tag}>(.*?)</{tag}>', r'\1', html)

        item.html_name = html
        self._on_item_changed(item)
        self._table_view.refresh()

    # Undo/Redo operaties
    def _save_undo_state(self, description: str = ""):
        """Sla huidige staat op voor undo"""
        if not self._schedule:
            return

        import copy
        # Maak een diepe kopie van de schedule data
        state = {
            'description': description,
            'schedule_data': self._schedule.to_dict() if hasattr(self._schedule, 'to_dict') else None
        }

        # Simpele state: bewaar item data
        if state['schedule_data'] is None:
            state['items_backup'] = []
            for item in self._schedule.get_all_items():
                state['items_backup'].append({
                    'id': id(item),
                    'name': item.name,
                    'html_name': item.html_name,
                    'identification': item.identification,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'sfb_code': item.sfb_code,
                    'is_text_only': item.is_text_only,
                })

        self._undo_stack.append(state)

        # Beperk stack grootte
        if len(self._undo_stack) > self._max_undo_levels:
            self._undo_stack.pop(0)

        # Clear redo stack bij nieuwe actie
        self._redo_stack.clear()

    def _undo(self):
        """Maak laatste actie ongedaan"""
        if not self._undo_stack:
            self._statusbar.showMessage("Niets om ongedaan te maken")
            return

        # Sla huidige staat op voor redo
        current_state = {
            'description': 'redo',
            'items_backup': []
        }
        if self._schedule:
            for item in self._schedule.get_all_items():
                current_state['items_backup'].append({
                    'id': id(item),
                    'name': item.name,
                    'html_name': item.html_name,
                    'identification': item.identification,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'sfb_code': item.sfb_code,
                    'is_text_only': item.is_text_only,
                })
        self._redo_stack.append(current_state)

        # Herstel vorige staat
        state = self._undo_stack.pop()

        if 'items_backup' in state and self._schedule:
            items_by_id = {id(item): item for item in self._schedule.get_all_items()}
            for backup in state['items_backup']:
                if backup['id'] in items_by_id:
                    item = items_by_id[backup['id']]
                    item.name = backup['name']
                    item.html_name = backup.get('html_name', '')
                    item.identification = backup['identification']
                    item.quantity = backup['quantity']
                    item.unit_price = backup['unit_price']
                    item.sfb_code = backup['sfb_code']
                    item.is_text_only = backup.get('is_text_only', False)

        self._table_view.refresh()
        self._update_totals()
        self._statusbar.showMessage("Ongedaan gemaakt")

    def _redo(self):
        """Voer laatste ongedaan gemaakte actie opnieuw uit"""
        if not self._redo_stack:
            self._statusbar.showMessage("Niets om opnieuw te doen")
            return

        # Sla huidige staat op voor undo
        current_state = {
            'description': 'undo',
            'items_backup': []
        }
        if self._schedule:
            for item in self._schedule.get_all_items():
                current_state['items_backup'].append({
                    'id': id(item),
                    'name': item.name,
                    'html_name': item.html_name,
                    'identification': item.identification,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'sfb_code': item.sfb_code,
                    'is_text_only': item.is_text_only,
                })
        self._undo_stack.append(current_state)

        # Herstel redo staat
        state = self._redo_stack.pop()

        if 'items_backup' in state and self._schedule:
            items_by_id = {id(item): item for item in self._schedule.get_all_items()}
            for backup in state['items_backup']:
                if backup['id'] in items_by_id:
                    item = items_by_id[backup['id']]
                    item.name = backup['name']
                    item.html_name = backup.get('html_name', '')
                    item.identification = backup['identification']
                    item.quantity = backup['quantity']
                    item.unit_price = backup['unit_price']
                    item.sfb_code = backup['sfb_code']
                    item.is_text_only = backup.get('is_text_only', False)

        self._table_view.refresh()
        self._update_totals()
        self._statusbar.showMessage("Opnieuw uitgevoerd")

    def _setup_menu(self):
        """Stel het menu in (minimaal, ribbon heeft meeste acties)"""
        menubar = self.menuBar()

        # Bestand menu
        file_menu = menubar.addMenu("&Bestand")

        self._new_action = QAction("&Nieuw", self)
        self._new_action.setShortcut(QKeySequence.New)
        self._new_action.triggered.connect(self._new_file)
        file_menu.addAction(self._new_action)

        self._open_action = QAction("&Openen...", self)
        self._open_action.setShortcut(QKeySequence.Open)
        self._open_action.triggered.connect(self._open_file)
        file_menu.addAction(self._open_action)

        file_menu.addSeparator()

        self._save_action = QAction("Op&slaan", self)
        self._save_action.setShortcut(QKeySequence.Save)
        self._save_action.triggered.connect(self._save_file)
        file_menu.addAction(self._save_action)

        self._save_as_action = QAction("Opslaan &als...", self)
        self._save_as_action.setShortcut(QKeySequence.SaveAs)
        self._save_as_action.triggered.connect(self._save_file_as)
        file_menu.addAction(self._save_as_action)

        file_menu.addSeparator()

        self._exit_action = QAction("&Afsluiten", self)
        self._exit_action.setShortcut(QKeySequence.Quit)
        self._exit_action.triggered.connect(self.close)
        file_menu.addAction(self._exit_action)

        # Bewerken menu
        edit_menu = menubar.addMenu("&Bewerken")

        self._undo_action = QAction("&Ongedaan maken", self)
        self._undo_action.setShortcut(QKeySequence.Undo)
        self._undo_action.triggered.connect(self._undo)
        edit_menu.addAction(self._undo_action)

        self._redo_action = QAction("O&pnieuw", self)
        self._redo_action.setShortcut(QKeySequence.Redo)
        self._redo_action.triggered.connect(self._redo)
        edit_menu.addAction(self._redo_action)

        edit_menu.addSeparator()

        self._cut_action = QAction("K&nippen", self)
        self._cut_action.setShortcut(QKeySequence.Cut)
        self._cut_action.triggered.connect(self._cut_item)
        edit_menu.addAction(self._cut_action)

        self._copy_action = QAction("&Kopiëren", self)
        self._copy_action.setShortcut(QKeySequence.Copy)
        self._copy_action.triggered.connect(self._copy_item)
        edit_menu.addAction(self._copy_action)

        self._paste_action = QAction("&Plakken", self)
        self._paste_action.setShortcut(QKeySequence.Paste)
        self._paste_action.triggered.connect(self._paste_item)
        edit_menu.addAction(self._paste_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        self._about_action = QAction("&Over OpenCalc...", self)
        self._about_action.triggered.connect(self._show_about)
        help_menu.addAction(self._about_action)

    def _setup_statusbar(self):
        """Stel de statusbalk in"""
        self._statusbar = QStatusBar()
        self.setStatusBar(self._statusbar)
        self._statusbar.showMessage("Gereed")

    def _connect_signals(self):
        """Verbind signalen"""
        # Tabel signalen voor huidige tab
        doc_widget = self._current_doc_widget
        if doc_widget:
            self._table_view = doc_widget.table_view
            self._surcharges_panel = doc_widget.surcharges_panel
            self._table_view.itemSelected.connect(self._on_item_selected)
            self._table_view.itemChanged.connect(self._on_item_changed)

        # Ribbon signalen
        self._ribbon.newFile.connect(self._new_file)
        self._ribbon.openFile.connect(self._open_file)
        self._ribbon.saveFile.connect(self._save_file)
        self._ribbon.saveFileAs.connect(self._save_file_as)
        self._ribbon.printPreview.connect(self._print_preview)
        self._ribbon.printFile.connect(self._print)
        self._ribbon.exportPdf.connect(self._export_pdf)
        self._ribbon.exportHtml.connect(self._export_html)
        self._ribbon.exportXls.connect(self._export_xls)
        self._ribbon.exportOds.connect(self._export_ods)
        self._ribbon.exportOdt.connect(self._export_odt)

        self._ribbon.addChapter.connect(self._add_chapter)
        self._ribbon.addCostItem.connect(self._add_cost_item)
        self._ribbon.addTextRow.connect(self._add_text_row)

        # Undo/Redo signalen
        self._ribbon.undoAction.connect(self._undo)
        self._ribbon.redoAction.connect(self._redo)

        # Clipboard signalen
        self._ribbon.cutItem.connect(self._cut_item)
        self._ribbon.copyItem.connect(self._copy_item)
        self._ribbon.pasteItem.connect(self._paste_item)

        # Tekst opmaak signalen
        self._ribbon.formatBold.connect(self._toggle_bold)
        self._ribbon.formatItalic.connect(self._toggle_italic)
        self._ribbon.formatUnderline.connect(self._toggle_underline)
        self._ribbon.formatColor.connect(self._set_text_color)

        # Document viewer signalen
        self._ribbon.openPdf.connect(self._doc_viewer.open_pdf)
        self._ribbon.openIfc.connect(self._doc_viewer.open_ifc)
        self._ribbon.openDxf.connect(self._doc_viewer.open_dxf)

        # IFC 3D viewer signaal
        self._ribbon.openIfc3D.connect(self._open_ifc_3d)

        # Import signalen
        self._ribbon.importExcel.connect(self._import_excel)
        self._ribbon.importCsv.connect(self._import_csv)

        # Panel toggle signalen
        self._ribbon._toggle_props_btn.toggled.connect(self._properties_dock.setVisible)
        self._ribbon._toggle_docs_btn.toggled.connect(self._toggle_doc_viewer)

        # Dark mode signaal
        self._ribbon.toggleDarkMode.connect(self._toggle_dark_mode)

        # Properties panel signaal
        self._properties_panel.itemChanged.connect(self._on_item_changed)

        # Zet documenten toggle standaard uit
        self._ribbon._toggle_docs_btn.setChecked(False)

    def _update_title(self):
        """Update de venstertitel en tab titel"""
        title = "OpenCalc"
        tab_title = "Nieuwe Begroting"

        if self._ifc_handler.file_path:
            tab_title = self._ifc_handler.file_path.stem  # Bestandsnaam zonder extensie
            title = f"{self._ifc_handler.file_path.name} - {title}"
        elif self._schedule:
            tab_title = self._schedule.name
            title = f"{self._schedule.name} - {title}"

        if self._ifc_handler.is_modified:
            title = f"* {title}"
            tab_title = f"* {tab_title}"

        self.setWindowTitle(title)

        # Update huidige tab titel
        current_idx = self._document_tabs.currentIndex()
        if current_idx >= 0:
            self._document_tabs.setTabText(current_idx, tab_title)

    def _update_totals(self):
        """Update het opslagen paneel"""
        self._surcharges_panel.set_schedule(self._schedule)

    # =========================================================================
    # BESTAND OPERATIES
    # =========================================================================

    def _new_file(self):
        """Maak een nieuw bestand"""
        if not self._check_save():
            return

        # Maak nieuw IFC bestand
        self._ifc_handler.new_file()
        self._cost_api = CostAPI(self._ifc_handler.ifc_file)

        # Maak nieuwe begroting
        self._schedule = CostSchedule(name="Nieuwe Begroting")

        # Maak IFC cost schedule
        ifc_schedule = self._cost_api.add_cost_schedule(
            name=self._schedule.name,
            predefined_type="BUDGET"
        )
        self._schedule.ifc_cost_schedule = ifc_schedule

        # Update UI
        self._table_view.set_schedule(self._schedule)
        # Update document tab
        if self._current_doc_widget:
            self._current_doc_widget.schedule = self._schedule
            # Update report panel en quotation panel met schedule
            self._current_doc_widget.report_panel.set_schedule(self._schedule)
            self._current_doc_widget.quotation_panel.set_schedule(self._schedule)

        self._update_title()
        self._update_totals()
        self._statusbar.showMessage("Nieuwe begroting aangemaakt")

    def _open_file(self):
        """Open een bestaand bestand via dialoog"""
        if not self._check_save():
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "IFC Bestand Openen",
            "",
            "IFC Bestanden (*.ifc);;Alle Bestanden (*.*)"
        )

        if file_path:
            self._open_file_path(file_path)

    def _open_file_path(self, file_path: str):
        """Open een bestand op een specifiek pad"""
        try:
            self._ifc_handler.open_file(file_path)
            self._cost_api = CostAPI(self._ifc_handler.ifc_file)
            self._load_schedule_from_ifc()
            self._update_title()
            self._update_totals()
            self._statusbar.showMessage(f"Geopend: {file_path}")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Fout bij openen",
                f"Kan bestand niet openen:\n{str(e)}"
            )

    def _save_file(self):
        """Sla het bestand op"""
        if not self._ifc_handler.file_path:
            self._save_file_as()
        else:
            self._do_save()

    def _save_file_as(self):
        """Sla het bestand op onder een nieuwe naam"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Begroting Opslaan",
            "",
            "IFC Bestanden (*.ifc)"
        )

        if file_path:
            self._do_save(file_path)

    def _do_save(self, file_path: Optional[str] = None):
        """Voer het opslaan uit"""
        try:
            # Sync model naar IFC
            self._sync_schedule_to_ifc()

            # Sla op
            saved_path = self._ifc_handler.save_file(file_path)
            self._update_title()
            self._statusbar.showMessage(f"Opgeslagen: {saved_path}")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Fout bij opslaan",
                f"Kan bestand niet opslaan:\n{str(e)}"
            )

    def _check_save(self) -> bool:
        """Controleer of wijzigingen moeten worden opgeslagen"""
        if self._ifc_handler.is_modified:
            reply = QMessageBox.question(
                self,
                "Wijzigingen opslaan?",
                "Het bestand is gewijzigd. Wilt u de wijzigingen opslaan?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            if reply == QMessageBox.Save:
                self._save_file()
                return not self._ifc_handler.is_modified
            elif reply == QMessageBox.Cancel:
                return False
        return True

    def _load_schedule_from_ifc(self):
        """Laad de begroting vanuit het IFC bestand"""
        schedules = self._ifc_handler.get_cost_schedules()
        print(f"DEBUG: Gevonden schedules: {len(schedules)}")
        if schedules:
            ifc_schedule = schedules[0]
            self._schedule = CostSchedule.from_ifc(ifc_schedule)
            print(f"DEBUG: Schedule naam: {self._schedule.name}")

            # Laad items recursief
            root_items = self._cost_api.get_root_cost_items(ifc_schedule)
            print(f"DEBUG: Root items: {len(root_items)}")
            for ifc_item in root_items:
                item = self._load_cost_item_recursive(ifc_item)
                self._schedule.add_item(item)
            print(f"DEBUG: Items na laden: {len(self._schedule.items)}")
            print(f"DEBUG: Subtotaal: {self._schedule.subtotal}")
        else:
            # Maak nieuwe schedule als er geen bestaat
            self._schedule = CostSchedule(name="Nieuwe Begroting")
            ifc_schedule = self._cost_api.add_cost_schedule(
                name=self._schedule.name
            )
            self._schedule.ifc_cost_schedule = ifc_schedule

        self._table_view.set_schedule(self._schedule)
        # Update document tab
        if self._current_doc_widget:
            self._current_doc_widget.schedule = self._schedule
            # Update report panel en quotation panel met schedule
            self._current_doc_widget.report_panel.set_schedule(self._schedule)
            self._current_doc_widget.quotation_panel.set_schedule(self._schedule)

            # Laad projectgegevens uit IFC
            project_data = self._cost_api.load_project_data()
            if project_data:
                self._current_doc_widget.project_panel.set_project_data(project_data)

        self._update_totals()  # Update totalen balk

    def _load_cost_item_recursive(
        self,
        ifc_item,
        parent: Optional[CostItem] = None
    ) -> CostItem:
        """Laad een cost item recursief"""
        item = CostItem.from_ifc(ifc_item, parent)

        # Laad SFB-code uit IFC properties
        sfb_code = self._cost_api.get_sfb_code(ifc_item)
        if sfb_code:
            item.sfb_code = sfb_code

        # Laad HTML opmaak uit IFC properties
        html_name = self._cost_api.get_html_name(ifc_item)
        if html_name:
            item.html_name = html_name

        # Laad is_text_only markering uit IFC properties
        is_text_only = self._cost_api.get_is_text_only(ifc_item)
        if is_text_only:
            item.is_text_only = True

        # Laad kinderen
        nested = self._cost_api.get_nested_cost_items(ifc_item)
        for ifc_child in nested:
            child = self._load_cost_item_recursive(ifc_child, item)
            item.add_child(child)

        return item

    def _sync_schedule_to_ifc(self):
        """Synchroniseer het model naar het IFC bestand"""
        if not self._schedule or not self._cost_api:
            return

        # Update schedule attributen
        if self._schedule.ifc_cost_schedule:
            self._cost_api.edit_cost_schedule(
                self._schedule.ifc_cost_schedule,
                {"Name": self._schedule.name}
            )

        # Sync alle items recursief (inclusief SFB codes)
        for item in self._schedule.get_all_items():
            self._sync_item_to_ifc(item)

        # Sla projectgegevens op in IFC
        if self._current_doc_widget and hasattr(self._current_doc_widget, 'project_panel'):
            project_data = self._current_doc_widget.project_panel.get_project_data()
            self._cost_api.save_project_data(project_data)

    def _sync_item_to_ifc(self, item: CostItem):
        """Sync een CostItem naar IFC"""
        if not item.ifc_cost_item or not self._cost_api:
            return

        # Update item attributen
        self._cost_api.edit_cost_item(
            item.ifc_cost_item,
            {
                "Name": item.name,
                "Identification": item.identification,
                "Description": item.description
            }
        )

        # Sla SFB-code op in IFC properties
        if item.sfb_code:
            self._cost_api.set_sfb_code(item.ifc_cost_item, item.sfb_code)

        # Sla HTML opmaak op in IFC properties
        if item.html_name:
            self._cost_api.set_html_name(item.ifc_cost_item, item.html_name)

        # Sla is_text_only op in IFC properties
        if item.is_text_only:
            self._cost_api.set_is_text_only(item.ifc_cost_item, True)

    # =========================================================================
    # ITEM OPERATIES
    # =========================================================================

    def _add_chapter(self):
        """Voeg een nieuw hoofdstuk toe op de cursor positie"""
        if not self._schedule:
            return

        # Bepaal positie op basis van selectie
        selected = self._table_view.get_selected_item()
        insert_index = len(self._schedule.items)  # Default: achteraan

        if selected:
            # Zoek het root hoofdstuk van het geselecteerde item
            root_item = selected
            while root_item.parent:
                root_item = root_item.parent

            # Vind de index van dit hoofdstuk
            if root_item in self._schedule.items:
                insert_index = self._schedule.items.index(root_item) + 1

        # Maak nieuw hoofdstuk
        chapter = CostItem(
            name="Nieuw Hoofdstuk",
            identification=f"{insert_index + 1:02d}"
        )
        chapter.schedule = self._schedule

        # Voeg in op de juiste positie
        self._schedule.items.insert(insert_index, chapter)

        # Hernummer alle hoofdstukken
        for i, item in enumerate(self._schedule.items):
            item.identification = f"{i + 1:02d}"

        # Maak IFC item
        if self._cost_api and self._schedule.ifc_cost_schedule:
            ifc_item = self._cost_api.add_cost_item(
                cost_schedule=self._schedule.ifc_cost_schedule,
                name=chapter.name,
                identification=chapter.identification
            )
            chapter.ifc_cost_item = ifc_item

        self._ifc_handler.mark_modified()
        self._table_view.refresh()
        self._table_view.select_item(chapter)  # Selecteer het nieuwe hoofdstuk
        self._update_title()
        self._update_totals()
        self._statusbar.showMessage("Hoofdstuk toegevoegd")

    def _add_cost_item(self):
        """Voeg een nieuwe kostenpost toe"""
        if not self._schedule:
            return

        # Bepaal parent (geselecteerd item of eerste hoofdstuk)
        selected = self._table_view.get_selected_item()
        if selected:
            parent = selected
        elif self._schedule.items:
            parent = self._schedule.items[0]
        else:
            # Maak eerst een hoofdstuk
            self._add_chapter()
            parent = self._schedule.items[0]

        item = CostItem(
            name="Nieuwe Post",
            identification=f"{len(parent.children) + 1:02d}"
        )
        parent.add_child(item)

        # Maak IFC item
        if self._cost_api and parent.ifc_cost_item:
            ifc_item = self._cost_api.add_cost_item(
                cost_item=parent.ifc_cost_item,
                name=item.name,
                identification=item.identification
            )
            item.ifc_cost_item = ifc_item

        self._ifc_handler.mark_modified()
        self._table_view.refresh()
        self._update_title()
        self._update_totals()
        self._statusbar.showMessage("Kostenpost toegevoegd")

    def _add_text_row(self):
        """Voeg een tekstregel toe (zonder hoeveelheid/kosten)"""
        if not self._schedule:
            return

        # Bepaal parent (geselecteerd item of eerste hoofdstuk)
        selected = self._table_view.get_selected_item()
        if selected:
            parent = selected
        elif self._schedule.items:
            parent = self._schedule.items[0]
        else:
            # Maak eerst een hoofdstuk
            self._add_chapter()
            parent = self._schedule.items[0]

        item = CostItem(
            name="Tekstregel",
            identification="",  # Geen identificatie voor tekstregels
            is_text_only=True
        )
        parent.add_child(item)

        # Maak IFC item
        if self._cost_api and parent.ifc_cost_item:
            ifc_item = self._cost_api.add_cost_item(
                cost_item=parent.ifc_cost_item,
                name=item.name,
                identification=item.identification
            )
            item.ifc_cost_item = ifc_item
            # Sla is_text_only op in IFC
            self._cost_api.set_is_text_only(ifc_item, True)

        self._ifc_handler.mark_modified()
        self._table_view.refresh()
        self._update_title()
        self._update_totals()
        self._statusbar.showMessage("Tekstregel toegevoegd")

    def _on_item_selected(self, item: Optional[CostItem]):
        """Afhandeling van item selectie"""
        # Update properties panel
        self._properties_panel.set_item(item)
        self.selectionChanged.emit(item)

    def _on_item_changed(self, item: CostItem):
        """Afhandeling van item wijziging"""
        # Prevent re-entry
        if getattr(self, '_updating_item', False):
            return
        self._updating_item = True

        try:
            # Update IFC
            if self._cost_api and item.ifc_cost_item:
                self._cost_api.edit_cost_item(
                    item.ifc_cost_item,
                    {
                        "Name": item.name,
                        "Identification": item.identification,
                        "Description": item.description
                    }
                )
                # Sla SFB-code op in IFC properties
                if item.sfb_code:
                    self._cost_api.set_sfb_code(item.ifc_cost_item, item.sfb_code)

                # Sla HTML opmaak op in IFC properties
                if item.html_name:
                    self._cost_api.set_html_name(item.ifc_cost_item, item.html_name)

                # Sla is_text_only op in IFC properties
                if item.is_text_only:
                    self._cost_api.set_is_text_only(item.ifc_cost_item, True)

            self._ifc_handler.mark_modified()
            # Don't call refresh() here - it causes infinite loop
            # The model already has the updated data
            self._update_title()
            self._update_totals()
        finally:
            self._updating_item = False

    def _show_about(self):
        """Toon het over dialoog"""
        QMessageBox.about(
            self,
            "Over OpenCalc",
            "OpenCalc v0.2.0\n\n"
            "Open source kostenbegrotingsprogramma\n"
            "IFC als native bestandsformaat\n\n"
            "Features:\n"
            "• Hiërarchische begrotingsstructuur\n"
            "• PDF, IFC en DXF/DWG viewer\n"
            "• Maatvoering op tekeningen\n"
            "• PDF en HTML export\n\n"
            "Gebouwd met Python, PySide6 en IfcOpenShell"
        )

    # =========================================================================
    # PRINT EN EXPORT OPERATIES
    # =========================================================================

    def _print_preview(self):
        """Toon afdrukvoorbeeld"""
        if not self._schedule:
            QMessageBox.warning(self, "Geen begroting", "Er is geen begroting om af te drukken.")
            return

        from ..services import PrintService
        print_service = PrintService(self._schedule)
        print_service.print_preview(self)

    def _print(self):
        """Direct afdrukken"""
        if not self._schedule:
            QMessageBox.warning(self, "Geen begroting", "Er is geen begroting om af te drukken.")
            return

        from ..services import PrintService
        print_service = PrintService(self._schedule)
        if print_service.print_direct(self):
            self._statusbar.showMessage("Afdrukken voltooid")

    def _export_pdf(self):
        """Exporteer naar PDF"""
        if not self._schedule:
            QMessageBox.warning(self, "Geen begroting", "Er is geen begroting om te exporteren.")
            return

        # Bepaal standaard bestandsnaam
        default_name = self._schedule.name.replace(" ", "_") + ".pdf"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporteer als PDF",
            default_name,
            "PDF Bestanden (*.pdf)"
        )

        if file_path:
            from ..services import PrintService
            print_service = PrintService(self._schedule)
            if print_service.export_pdf(file_path):
                self._statusbar.showMessage(f"PDF geëxporteerd: {file_path}")
                QMessageBox.information(
                    self,
                    "Export Succesvol",
                    f"De begroting is geëxporteerd naar:\n{file_path}"
                )
            else:
                QMessageBox.critical(
                    self,
                    "Export Mislukt",
                    "Er is een fout opgetreden bij het exporteren naar PDF."
                )

    def _toggle_doc_viewer(self, visible: bool):
        """Toggle de document viewer zichtbaarheid"""
        self._doc_viewer.setVisible(visible)
        if visible:
            # Pas splitter verhoudingen aan (2 panelen: doc viewer | tabs)
            sizes = self._main_splitter.sizes()
            total = sum(sizes)
            new_sizes = [int(total * 0.4), int(total * 0.6)]
            self._main_splitter.setSizes(new_sizes)

    def _toggle_dark_mode(self, enabled: bool):
        """Toggle next-level dark mode thema"""
        if enabled:
            dark_style = """
                /* ===== NEXT LEVEL DARK MODE ===== */
                * { color: #e2e8f0; }

                QMainWindow { background-color: #0a0f1a; }
                QWidget { background-color: #111827; color: #e2e8f0; }

                /* Menu */
                QMenuBar {
                    background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #1f2937, stop:1 #111827);
                    color: #e2e8f0; border-bottom: 1px solid #374151;
                }
                QMenuBar::item:selected { background: #374151; border-radius: 4px; }
                QMenu { background: #1f2937; border: 1px solid #4b5563; border-radius: 8px; padding: 4px; }
                QMenu::item { padding: 8px 20px; border-radius: 4px; }
                QMenu::item:selected { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #0ea5e9, stop:1 #06b6d4); }

                /* Tabs */
                QTabWidget::pane { background: #111827; border: none; border-top: 2px solid #0ea5e9; }
                QTabBar::tab { background: transparent; color: #9ca3af; padding: 10px 20px; font-weight: 500; }
                QTabBar::tab:selected { color: #0ea5e9; border-bottom: 3px solid #0ea5e9; background: #1f2937; }
                QTabBar::tab:hover:!selected { background: #1f2937; color: #e2e8f0; }

                /* Tree/Table Views */
                QTreeView, QTableView, QTableWidget, QListView {
                    background: #0a0f1a; color: #e2e8f0; border: 1px solid #374151;
                    border-radius: 8px; alternate-background-color: #111827;
                    gridline-color: #1f2937;
                }
                QTreeView::item, QTableView::item { padding: 8px; border-bottom: 1px solid #1f2937; }
                QTreeView::item:selected, QTableView::item:selected {
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #0369a1, stop:1 #0ea5e9);
                    color: white;
                }
                QTreeView::item:hover:!selected { background: #1e3a5f; }
                QHeaderView::section {
                    background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #374151, stop:1 #1f2937);
                    color: #9ca3af; border: none; border-right: 1px solid #4b5563;
                    border-bottom: 1px solid #4b5563; padding: 10px; font-weight: 600;
                }

                /* Inputs */
                QLineEdit, QTextEdit, QPlainTextEdit, QTextBrowser {
                    background: #0a0f1a; color: #e2e8f0; border: 2px solid #374151;
                    border-radius: 8px; padding: 10px;
                }
                QLineEdit:focus, QTextEdit:focus { border: 2px solid #0ea5e9; background: #111827; }
                QSpinBox, QDoubleSpinBox, QDateEdit, QComboBox {
                    background: #0a0f1a; color: #e2e8f0; border: 2px solid #374151;
                    border-radius: 8px; padding: 8px;
                }
                QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus, QComboBox:focus { border: 2px solid #0ea5e9; }
                QComboBox::drop-down { border: none; background: #374151; width: 30px; border-radius: 0 6px 6px 0; }
                QComboBox QAbstractItemView { background: #1f2937; border: 1px solid #4b5563; border-radius: 8px; }

                /* Buttons */
                QPushButton {
                    background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #4b5563, stop:1 #374151);
                    color: #e2e8f0; border: 1px solid #6b7280; border-radius: 8px; padding: 10px 18px; font-weight: 500;
                }
                QPushButton:hover { background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #6b7280, stop:1 #4b5563); }
                QPushButton:pressed { background: #1f2937; border: 1px solid #0ea5e9; }
                QToolButton { background: transparent; color: #e2e8f0; border-radius: 6px; padding: 6px; }
                QToolButton:hover { background: #374151; }
                QToolButton:checked { background: #0ea5e9; color: white; }

                /* GroupBox */
                QGroupBox {
                    background: #1f2937; border: 1px solid #374151; border-radius: 12px;
                    margin-top: 20px; padding: 20px; padding-top: 28px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin; left: 16px; padding: 0 10px;
                    color: #0ea5e9; background: #1f2937; font-weight: 600;
                }

                /* Checkbox/Radio */
                QCheckBox, QRadioButton { color: #e2e8f0; spacing: 10px; }
                QCheckBox::indicator, QRadioButton::indicator {
                    width: 22px; height: 22px; border: 2px solid #4b5563; border-radius: 6px; background: #0a0f1a;
                }
                QRadioButton::indicator { border-radius: 11px; }
                QCheckBox::indicator:checked, QRadioButton::indicator:checked { background: #0ea5e9; border-color: #0ea5e9; }
                QCheckBox::indicator:hover { border-color: #0ea5e9; }

                /* Scrollbars */
                QScrollBar:vertical { background: #0a0f1a; width: 14px; border-radius: 7px; }
                QScrollBar::handle:vertical {
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #4b5563, stop:1 #6b7280);
                    border-radius: 6px; min-height: 30px; margin: 2px;
                }
                QScrollBar::handle:vertical:hover { background: #0ea5e9; }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
                QScrollBar:horizontal { background: #0a0f1a; height: 14px; border-radius: 7px; }
                QScrollBar::handle:horizontal {
                    background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #4b5563, stop:1 #6b7280);
                    border-radius: 6px; min-width: 30px; margin: 2px;
                }
                QScrollBar::handle:horizontal:hover { background: #0ea5e9; }
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

                /* Status & Dock */
                QStatusBar { background: #0a0f1a; color: #9ca3af; border-top: 1px solid #374151; }
                QDockWidget { color: #e2e8f0; }
                QDockWidget::title {
                    background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #374151, stop:1 #1f2937);
                    color: #0ea5e9; padding: 12px; border-bottom: 2px solid #0ea5e9; font-weight: 600;
                }

                /* Misc */
                QLabel { color: #e2e8f0; background: transparent; }
                QFrame { border-color: #374151; }
                QSplitter::handle { background: #374151; }
                QSplitter::handle:hover { background: #0ea5e9; }
                QToolTip { background: #1f2937; color: #e2e8f0; border: 1px solid #0ea5e9; border-radius: 6px; padding: 8px; }
                QScrollArea { background: transparent; border: none; }
                QDialog { background: #1f2937; }
            """
            self.setStyleSheet(dark_style)
            self._is_dark_mode = True
        else:
            self.setStyleSheet("")
            self._is_dark_mode = False

    def _open_ifc_3d(self):
        """Open de IFC 3D viewer in het documenten paneel"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "IFC 3D Model Openen",
            "",
            "IFC Bestanden (*.ifc);;Alle Bestanden (*.*)"
        )

        if file_path:
            # Toon het documenten paneel en open het IFC bestand
            self._doc_viewer.show()
            self._doc_viewer.open_file(file_path)

            # Pas splitter verhoudingen aan
            sizes = self._main_splitter.sizes()
            total = sum(sizes)
            new_sizes = [int(total * 0.5), int(total * 0.5)]
            self._main_splitter.setSizes(new_sizes)

            self._statusbar.showMessage(f"3D model geladen: {Path(file_path).name}")

    def _export_html(self):
        """Exporteer naar HTML"""
        if not self._schedule:
            QMessageBox.warning(self, "Geen begroting", "Er is geen begroting om te exporteren.")
            return

        # Bepaal standaard bestandsnaam
        default_name = self._schedule.name.replace(" ", "_") + ".html"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporteer als HTML",
            default_name,
            "HTML Bestanden (*.html)"
        )

        if file_path:
            from ..services import PrintService
            print_service = PrintService(self._schedule)
            if print_service.export_html(file_path):
                self._statusbar.showMessage(f"HTML geëxporteerd: {file_path}")
                QMessageBox.information(
                    self,
                    "Export Succesvol",
                    f"De begroting is geëxporteerd naar:\n{file_path}"
                )
            else:
                QMessageBox.critical(
                    self,
                    "Export Mislukt",
                    "Er is een fout opgetreden bij het exporteren naar HTML."
                )


    def _export_xls(self):
        """Exporteer naar Excel"""
        if not self._schedule:
            QMessageBox.warning(self, "Geen begroting", "Er is geen begroting om te exporteren.")
            return

        default_name = self._schedule.name.replace(" ", "_") + ".xlsx"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporteer als Excel",
            default_name,
            "Excel Bestanden (*.xlsx)"
        )

        if file_path:
            from ..services import ExportService
            export_service = ExportService(self._schedule)
            if export_service.export_xlsx(file_path):
                self._statusbar.showMessage(f"Excel geexporteerd: {file_path}")
                # Open bestand (cross-platform)
                self._open_file_external(file_path)
            else:
                QMessageBox.critical(self, "Export Mislukt", "Er is een fout opgetreden.")

    def _export_ods(self):
        """Exporteer naar ODS"""
        if not self._schedule:
            QMessageBox.warning(self, "Geen begroting", "Er is geen begroting om te exporteren.")
            return

        default_name = self._schedule.name.replace(" ", "_") + ".ods"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporteer als ODS",
            default_name,
            "ODS Bestanden (*.ods)"
        )

        if file_path:
            from ..services import ExportService
            export_service = ExportService(self._schedule)
            if export_service.export_ods(file_path):
                self._statusbar.showMessage(f"ODS geexporteerd: {file_path}")
                # Open bestand (cross-platform)
                self._open_file_external(file_path)
            else:
                QMessageBox.critical(self, "Export Mislukt", "Er is een fout opgetreden.")

    def _export_odt(self):
        """Exporteer naar ODT (LibreOffice Writer)"""
        if not self._schedule:
            QMessageBox.warning(self, "Geen begroting", "Er is geen begroting om te exporteren.")
            return

        default_name = self._schedule.name.replace(" ", "_") + ".odt"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporteer als ODT",
            default_name,
            "ODT Bestanden (*.odt)"
        )

        if file_path:
            from ..services import ExportService
            export_service = ExportService(self._schedule)
            if export_service.export_odt(file_path):
                self._statusbar.showMessage(f"ODT geexporteerd: {file_path}")
                # Open bestand in Writer
                self._open_file_external(file_path)
            else:
                QMessageBox.critical(self, "Export Mislukt", "Er is een fout opgetreden.")

    def _import_excel(self):
        """Importeer gegevens uit Excel bestand"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Excel Importeren",
            "",
            "Excel Bestanden (*.xlsx *.xls);;Alle Bestanden (*.*)"
        )

        if file_path:
            try:
                import openpyxl
                wb = openpyxl.load_workbook(file_path)
                ws = wb.active

                # Lees data en voeg toe aan begroting
                row_count = 0
                for row in ws.iter_rows(min_row=2, values_only=True):
                    if row[0]:  # Als er een code is
                        row_count += 1

                self._statusbar.showMessage(f"Excel geimporteerd: {row_count} regels uit {Path(file_path).name}")
                QMessageBox.information(
                    self,
                    "Import Succesvol",
                    f"Er zijn {row_count} regels geimporteerd uit:\n{file_path}"
                )
            except ImportError:
                QMessageBox.warning(
                    self,
                    "Module niet gevonden",
                    "openpyxl is niet geinstalleerd.\nInstalleer met: pip install openpyxl"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Import Fout",
                    f"Fout bij importeren:\n{str(e)}"
                )

    def _import_csv(self):
        """Importeer gegevens uit CSV bestand"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "CSV Importeren",
            "",
            "CSV Bestanden (*.csv);;Alle Bestanden (*.*)"
        )

        if file_path:
            try:
                import csv
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    reader = csv.reader(f, delimiter=';')
                    header = next(reader, None)  # Skip header

                    row_count = sum(1 for row in reader if row)

                self._statusbar.showMessage(f"CSV geimporteerd: {row_count} regels uit {Path(file_path).name}")
                QMessageBox.information(
                    self,
                    "Import Succesvol",
                    f"Er zijn {row_count} regels geimporteerd uit:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Import Fout",
                    f"Fout bij importeren:\n{str(e)}"
                )

    def _open_file_external(self, file_path: str):
        """Open een bestand met de standaard applicatie (cross-platform)"""
        import subprocess
        import sys
        try:
            if sys.platform == 'win32':
                subprocess.Popen(['start', '', file_path], shell=True)
            elif sys.platform == 'darwin':  # macOS
                subprocess.Popen(['open', file_path])
            else:  # Linux en andere Unix-achtige systemen
                subprocess.Popen(['xdg-open', file_path])
        except Exception:
            pass  # Negeer fouten bij openen

    def closeEvent(self, event):
        """Afhandeling van sluiten"""
        if self._check_save():
            event.accept()
        else:
            event.ignore()
