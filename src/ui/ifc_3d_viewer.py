"""
IFC 3D Viewer - WebEngine-gebaseerde 3D IFC viewer met That Open Company
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolBar, QToolButton,
    QLabel, QFileDialog, QMessageBox, QSplitter, QTreeWidget,
    QTreeWidgetItem, QFrame, QSizePolicy
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings, QWebEnginePage
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtCore import Qt, Signal, Slot, QObject, QUrl, QFile, QIODevice
from PySide6.QtGui import QColor

from pathlib import Path
import base64
import json


class IFCViewerBridge(QObject):
    """Bridge tussen Qt en JavaScript voor communicatie"""

    modelLoaded = Signal(str)
    elementSelected = Signal(dict)
    viewerReady = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    @Slot(str)
    def onModelLoaded(self, filename: str):
        """Callback wanneer model geladen is"""
        self.modelLoaded.emit(filename)

    @Slot(str)
    def onElementSelected(self, json_data: str):
        """Callback wanneer element geselecteerd is"""
        try:
            data = json.loads(json_data)
            self.elementSelected.emit(data)
        except json.JSONDecodeError:
            pass

    @Slot()
    def onViewerReady(self):
        """Callback wanneer viewer klaar is"""
        self.viewerReady.emit()


class IFC3DViewer(QWidget):
    """3D IFC Viewer widget met That Open Company engine"""

    modelLoaded = Signal(str)
    elementSelected = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._current_file = None
        self._viewer_ready = False

        self._setup_ui()
        self._setup_bridge()
        self._load_viewer()

    def _setup_ui(self):
        """Setup de UI componenten"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        self._toolbar = QToolBar()
        self._toolbar.setStyleSheet("""
            QToolBar {
                background: #f5f5f5;
                border-bottom: 1px solid #ddd;
                padding: 4px;
                spacing: 4px;
            }
            QToolButton {
                padding: 6px 10px;
                border-radius: 4px;
                border: none;
            }
            QToolButton:hover {
                background: #e0e0e0;
            }
            QToolButton:pressed {
                background: #d0d0d0;
            }
        """)

        # Open knop
        self._open_btn = QToolButton()
        self._open_btn.setText("📂 Openen")
        self._open_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self._open_btn.clicked.connect(self._open_file)
        self._toolbar.addWidget(self._open_btn)

        self._toolbar.addSeparator()

        # View knoppen
        self._fit_btn = QToolButton()
        self._fit_btn.setText("🔲 Passend")
        self._fit_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self._fit_btn.clicked.connect(self._fit_view)
        self._toolbar.addWidget(self._fit_btn)

        self._top_btn = QToolButton()
        self._top_btn.setText("⬆ Boven")
        self._top_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self._top_btn.clicked.connect(lambda: self._set_view("top"))
        self._toolbar.addWidget(self._top_btn)

        self._front_btn = QToolButton()
        self._front_btn.setText("⏹ Voor")
        self._front_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self._front_btn.clicked.connect(lambda: self._set_view("front"))
        self._toolbar.addWidget(self._front_btn)

        self._iso_btn = QToolButton()
        self._iso_btn.setText("📦 3D")
        self._iso_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self._iso_btn.clicked.connect(lambda: self._set_view("iso"))
        self._toolbar.addWidget(self._iso_btn)

        layout.addWidget(self._toolbar)

        # Splitter voor viewer en properties
        self._splitter = QSplitter(Qt.Horizontal)

        # WebEngine viewer
        self._web_view = QWebEngineView()
        self._web_view.setMinimumSize(400, 300)

        # WebEngine settings
        settings = self._web_view.settings()
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)

        self._splitter.addWidget(self._web_view)

        # Properties panel
        self._props_panel = QFrame()
        self._props_panel.setFrameShape(QFrame.StyledPanel)
        self._props_panel.setMaximumWidth(250)
        self._props_panel.setMinimumWidth(200)

        props_layout = QVBoxLayout(self._props_panel)

        props_header = QLabel("Model Structuur")
        props_header.setStyleSheet("font-weight: bold; padding: 8px; background: #f0f0f0;")
        props_layout.addWidget(props_header)

        self._tree_widget = QTreeWidget()
        self._tree_widget.setHeaderHidden(True)
        self._tree_widget.setStyleSheet("""
            QTreeWidget {
                border: none;
                background: white;
            }
            QTreeWidget::item {
                padding: 4px;
            }
            QTreeWidget::item:hover {
                background: #e3f2fd;
            }
            QTreeWidget::item:selected {
                background: #2962ff;
                color: white;
            }
        """)
        props_layout.addWidget(self._tree_widget)

        self._splitter.addWidget(self._props_panel)
        self._splitter.setSizes([800, 200])

        layout.addWidget(self._splitter)

        # Status bar
        self._status = QLabel("Gereed - Sleep een IFC bestand of klik Openen")
        self._status.setStyleSheet("""
            padding: 6px 10px;
            background: #f8f9fa;
            border-top: 1px solid #ddd;
            color: #666;
        """)
        layout.addWidget(self._status)

    def _setup_bridge(self):
        """Setup de Qt-JS bridge"""
        self._bridge = IFCViewerBridge(self)
        self._channel = QWebChannel()
        self._channel.registerObject("qt", self._bridge)
        self._web_view.page().setWebChannel(self._channel)

        # Connect signals
        self._bridge.modelLoaded.connect(self._on_model_loaded)
        self._bridge.elementSelected.connect(self._on_element_selected)
        self._bridge.viewerReady.connect(self._on_viewer_ready)

    def _load_viewer(self):
        """Laad de HTML viewer"""
        # Zoek het HTML bestand - gebruik de simpele versie die stabieler is
        viewer_path = Path(__file__).parent.parent.parent / "resources" / "viewer" / "ifc_viewer_simple.html"

        # Fallback naar originele viewer als simpele niet bestaat
        if not viewer_path.exists():
            viewer_path = Path(__file__).parent.parent.parent / "resources" / "viewer" / "ifc_viewer.html"

        if viewer_path.exists():
            self._web_view.setUrl(QUrl.fromLocalFile(str(viewer_path)))
        else:
            # Fallback: inline HTML
            self._web_view.setHtml(self._get_fallback_html())

    def _get_fallback_html(self) -> str:
        """Fallback HTML als viewer bestand niet gevonden"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    margin: 0;
                    padding: 40px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    background: #1a1a2e;
                    color: #fff;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    text-align: center;
                }
                .container {
                    max-width: 400px;
                }
                h2 { color: #2962ff; }
                p { color: #888; line-height: 1.6; }
                .icon { font-size: 64px; margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">🏗️</div>
                <h2>IFC 3D Viewer</h2>
                <p>De 3D viewer vereist een internetverbinding voor het laden van de That Open Company bibliotheken.</p>
                <p>Sleep een IFC bestand hierheen om te bekijken.</p>
            </div>
        </body>
        </html>
        """

    def _open_file(self):
        """Open een IFC bestand via dialoog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "IFC Bestand Openen",
            "",
            "IFC Bestanden (*.ifc);;Alle Bestanden (*.*)"
        )

        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path: str):
        """Laad een IFC bestand in de viewer"""
        path = Path(file_path)

        if not path.exists():
            QMessageBox.warning(self, "Bestand niet gevonden",
                                f"Kan bestand niet vinden:\n{file_path}")
            return

        self._current_file = str(path)
        self._status.setText(f"Laden: {path.name}...")

        try:
            # Lees bestand en converteer naar base64
            with open(path, 'rb') as f:
                data = f.read()

            base64_data = base64.b64encode(data).decode('utf-8')

            # Stuur naar JavaScript
            js_code = f'window.loadIFCBuffer("{base64_data}", "{path.name}")'
            self._web_view.page().runJavaScript(js_code)

        except Exception as e:
            QMessageBox.critical(self, "Laadfout",
                                 f"Fout bij laden van IFC:\n{str(e)}")
            self._status.setText("Fout bij laden")

    def _fit_view(self):
        """Pas weergave aan zodat model past"""
        self._web_view.page().runJavaScript('document.getElementById("btn-fit").click()')

    def _set_view(self, view_type: str):
        """Stel camera view in"""
        views = {
            "top": "world.camera.controls.setLookAt(0, 50, 0, 0, 0, 0, true)",
            "front": "world.camera.controls.setLookAt(0, 10, 50, 0, 0, 0, true)",
            "right": "world.camera.controls.setLookAt(50, 10, 0, 0, 0, 0, true)",
            "iso": "world.camera.controls.setLookAt(30, 30, 30, 0, 0, 0, true)"
        }

        if view_type in views:
            self._web_view.page().runJavaScript(views[view_type])

    def _on_model_loaded(self, filename: str):
        """Callback wanneer model geladen is"""
        self._status.setText(f"Geladen: {filename}")
        self.modelLoaded.emit(filename)

        # Update tree widget met basis structuur
        self._tree_widget.clear()

        root = QTreeWidgetItem(["📁 " + filename])
        self._tree_widget.addTopLevelItem(root)

        # Voeg standaard categorieën toe
        categories = [
            ("🧱 Muren", "IfcWall"),
            ("⬜ Vloeren", "IfcSlab"),
            ("🚪 Deuren", "IfcDoor"),
            ("🪟 Ramen", "IfcWindow"),
            ("📐 Kolommen", "IfcColumn"),
            ("📏 Balken", "IfcBeam"),
            ("🏠 Daken", "IfcRoof"),
        ]

        for name, ifc_type in categories:
            item = QTreeWidgetItem([name])
            item.setData(0, Qt.UserRole, ifc_type)
            root.addChild(item)

        root.setExpanded(True)

    def _on_element_selected(self, data: dict):
        """Callback wanneer element geselecteerd is"""
        self.elementSelected.emit(data)

    def _on_viewer_ready(self):
        """Callback wanneer viewer klaar is"""
        self._viewer_ready = True
        self._status.setText("Viewer gereed")

    def toggle_properties(self, visible: bool):
        """Toon/verberg properties paneel"""
        self._props_panel.setVisible(visible)


class IFC3DViewerPanel(QWidget):
    """Paneel wrapper voor de IFC 3D viewer met header"""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f0f0f0, stop:1 #e0e0e0);
                border-bottom: 1px solid #ccc;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(8, 4, 8, 4)

        title = QLabel("🏗️ IFC 3D Viewer")
        title.setStyleSheet("font-weight: bold; font-size: 10pt;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Close knop
        close_btn = QToolButton()
        close_btn.setText("×")
        close_btn.setStyleSheet("""
            QToolButton {
                border: none;
                font-size: 16px;
                padding: 2px 6px;
            }
            QToolButton:hover {
                background: #ddd;
                border-radius: 3px;
            }
        """)
        close_btn.clicked.connect(self.hide)
        header_layout.addWidget(close_btn)

        layout.addWidget(header)

        # Viewer
        self._viewer = IFC3DViewer()
        layout.addWidget(self._viewer)

    def load_file(self, file_path: str):
        """Laad een IFC bestand"""
        self._viewer.load_file(file_path)

    @property
    def viewer(self) -> IFC3DViewer:
        return self._viewer
