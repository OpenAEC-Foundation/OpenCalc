"""
Document Viewer - Multi-format document viewer met PDF, IFC, DXF ondersteuning
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QScrollArea,
    QLabel, QToolBar, QSpinBox, QSlider, QComboBox, QFileDialog,
    QMessageBox, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QSplitter, QListWidget, QListWidgetItem, QFrame, QToolButton,
    QMenu, QSizePolicy, QRubberBand, QGraphicsLineItem, QGraphicsTextItem
)
from PySide6.QtCore import Qt, Signal, QPointF, QRectF, QSize, QLineF, QPoint, QRect
from PySide6.QtGui import (
    QPixmap, QImage, QPainter, QPen, QColor, QFont, QWheelEvent,
    QMouseEvent, QCursor, QBrush, QTransform
)

from pathlib import Path
from typing import Optional, List, Tuple
import math

# Lazy import voor IFC 3D viewer om circulaire imports te voorkomen
IFC3DViewer = None


class AnnotationItem:
    """Basis annotatie item"""
    pass


class MeasurementItem(AnnotationItem):
    """Maatvoering annotatie"""
    def __init__(self, start: QPointF, end: QPointF, distance: float):
        self.start = start
        self.end = end
        self.distance = distance


class TextAnnotationItem(AnnotationItem):
    """Tekst annotatie"""
    def __init__(self, position: QPointF, text: str, color: QColor = QColor(0, 0, 255)):
        self.position = position
        self.text = text
        self.color = color


class MeasurementOverlay(QWidget):
    """Overlay voor maatvoering en annotaties op documenten"""

    annotationAdded = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)

        self._measuring = False
        self._annotating = False
        self._start_point: Optional[QPointF] = None
        self._end_point: Optional[QPointF] = None
        self._annotations: List[AnnotationItem] = []
        self._scale = 1.0  # pixels per mm
        self._current_scale = 1.0  # view scale

    def set_scale(self, pixels_per_mm: float):
        """Stel de schaal in (pixels per mm in origineel document)"""
        self._scale = pixels_per_mm

    def set_view_scale(self, scale: float):
        """Stel de weergaveschaal in"""
        self._current_scale = scale

    def start_measuring(self):
        """Start maatvoering modus"""
        self._measuring = True
        self.setCursor(Qt.CrossCursor)

    def stop_measuring(self):
        """Stop maatvoering modus"""
        self._measuring = False
        self._start_point = None
        self._end_point = None
        self.setCursor(Qt.ArrowCursor)
        self.update()

    def start_annotating(self):
        """Start annotatie modus"""
        self._annotating = True
        self._measuring = False
        self.setCursor(Qt.IBeamCursor)

    def stop_annotating(self):
        """Stop annotatie modus"""
        self._annotating = False
        self.setCursor(Qt.ArrowCursor)
        self.update()

    def clear_measurements(self):
        """Wis alle metingen"""
        self._annotations = [a for a in self._annotations if not isinstance(a, MeasurementItem)]
        self.update()

    def clear_annotations(self):
        """Wis alle annotaties"""
        self._annotations = [a for a in self._annotations if not isinstance(a, TextAnnotationItem)]
        self.update()

    def clear_all(self):
        """Wis alles"""
        self._annotations.clear()
        self.update()

    def add_text_annotation(self, position: QPointF, text: str):
        """Voeg een tekst annotatie toe"""
        self._annotations.append(TextAnnotationItem(position, text))
        self.annotationAdded.emit()
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if self._measuring and event.button() == Qt.LeftButton:
            self._start_point = event.position()
            self._end_point = event.position()
            self.update()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._measuring and self._start_point:
            self._end_point = event.position()
            self.update()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._measuring and self._start_point and self._end_point:
            # Bereken afstand in mm
            dx = (self._end_point.x() - self._start_point.x()) / self._current_scale
            dy = (self._end_point.y() - self._start_point.y()) / self._current_scale
            distance_px = math.sqrt(dx*dx + dy*dy)
            distance_mm = distance_px / self._scale if self._scale > 0 else distance_px

            # Sla meting op als MeasurementItem
            self._annotations.append(MeasurementItem(
                QPointF(self._start_point),
                QPointF(self._end_point),
                distance_mm
            ))
            self._start_point = None
            self._end_point = None
            self.annotationAdded.emit()
            self.update()
        elif self._annotating and event.button() == Qt.LeftButton:
            # Open tekst invoer dialoog
            from PySide6.QtWidgets import QInputDialog
            text, ok = QInputDialog.getText(self, "Opmerking toevoegen", "Tekst:")
            if ok and text:
                self.add_text_annotation(event.position(), text)
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font)

        # Teken opgeslagen annotaties
        for annotation in self._annotations:
            if isinstance(annotation, MeasurementItem):
                pen = QPen(QColor(255, 0, 0), 2)
                painter.setPen(pen)
                self._draw_measurement(painter, annotation.start, annotation.end, annotation.distance)
            elif isinstance(annotation, TextAnnotationItem):
                self._draw_text_annotation(painter, annotation)

        # Teken huidige meting
        if self._measuring and self._start_point and self._end_point:
            pen = QPen(QColor(255, 0, 0), 2)
            painter.setPen(pen)
            dx = (self._end_point.x() - self._start_point.x()) / self._current_scale
            dy = (self._end_point.y() - self._start_point.y()) / self._current_scale
            distance_px = math.sqrt(dx*dx + dy*dy)
            distance_mm = distance_px / self._scale if self._scale > 0 else distance_px
            self._draw_measurement(painter, self._start_point, self._end_point, distance_mm)

    def _draw_measurement(self, painter: QPainter, start: QPointF, end: QPointF, distance: float):
        """Teken een meting met lijn en tekst"""
        # Lijn
        painter.drawLine(start, end)

        # Eindpunten
        painter.drawEllipse(start, 4, 4)
        painter.drawEllipse(end, 4, 4)

        # Tekst
        mid = QPointF((start.x() + end.x()) / 2, (start.y() + end.y()) / 2)
        text = f"{distance:.1f} mm" if distance < 1000 else f"{distance/1000:.2f} m"

        # Achtergrond voor tekst
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255, 200))
        text_rect = painter.fontMetrics().boundingRect(text)
        bg_rect = QRectF(mid.x() - text_rect.width()/2 - 4,
                         mid.y() - text_rect.height()/2 - 2,
                         text_rect.width() + 8,
                         text_rect.height() + 4)
        painter.drawRoundedRect(bg_rect, 3, 3)

        # Tekst
        painter.setPen(QColor(255, 0, 0))
        painter.drawText(bg_rect, Qt.AlignCenter, text)

    def _draw_text_annotation(self, painter: QPainter, annotation: TextAnnotationItem):
        """Teken een tekst annotatie"""
        pos = annotation.position
        text = annotation.text

        # Achtergrond
        font = QFont("Arial", 10)
        painter.setFont(font)
        text_rect = painter.fontMetrics().boundingRect(text)

        bg_rect = QRectF(pos.x() - 2,
                         pos.y() - text_rect.height() - 2,
                         text_rect.width() + 12,
                         text_rect.height() + 8)

        # Gele sticky note achtergrond
        painter.setPen(QPen(QColor(200, 180, 0), 1))
        painter.setBrush(QColor(255, 255, 200, 230))
        painter.drawRoundedRect(bg_rect, 4, 4)

        # Pin/marker
        painter.setBrush(QColor(255, 100, 100))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(pos, 5, 5)

        # Tekst
        painter.setPen(QColor(60, 60, 60))
        painter.drawText(bg_rect.adjusted(4, 2, -4, -2), Qt.AlignCenter, text)


class DocumentGraphicsView(QGraphicsView):
    """Graphics view met zoom en pan functionaliteit"""

    scaleChanged = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene()
        self.setScene(self._scene)

        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setBackgroundBrush(QBrush(QColor(64, 64, 64)))

        self._current_scale = 1.0
        self._pixmap_item: Optional[QGraphicsPixmapItem] = None
        self._measurement_overlay: Optional[MeasurementOverlay] = None

    def set_pixmap(self, pixmap: QPixmap):
        """Stel de weer te geven afbeelding in"""
        self._scene.clear()
        self._pixmap_item = self._scene.addPixmap(pixmap)
        self.setSceneRect(pixmap.rect().toRectF())
        self.fit_in_view()

    def fit_in_view(self):
        """Pas de weergave aan zodat het document past"""
        if self._pixmap_item:
            self.fitInView(self._pixmap_item, Qt.KeepAspectRatio)
            self._current_scale = self.transform().m11()
            self.scaleChanged.emit(self._current_scale)

    def zoom_in(self):
        """Zoom in"""
        self.scale(1.25, 1.25)
        self._current_scale *= 1.25
        self.scaleChanged.emit(self._current_scale)

    def zoom_out(self):
        """Zoom uit"""
        self.scale(0.8, 0.8)
        self._current_scale *= 0.8
        self.scaleChanged.emit(self._current_scale)

    def set_zoom(self, scale: float):
        """Stel zoom niveau in"""
        factor = scale / self._current_scale
        self.scale(factor, factor)
        self._current_scale = scale
        self.scaleChanged.emit(self._current_scale)

    def wheelEvent(self, event: QWheelEvent):
        """Zoom met muiswiel"""
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def get_current_scale(self) -> float:
        return self._current_scale


class PDFViewer(QWidget):
    """PDF document viewer"""

    pageChanged = Signal(int, int)  # current, total

    def __init__(self, parent=None):
        super().__init__(parent)
        self._doc = None
        self._fitz = None  # PyMuPDF module reference
        self._current_page = 0
        self._total_pages = 0
        self._dpi = 150

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(16, 16))

        # Pagina navigatie
        self._prev_btn = QToolButton()
        self._prev_btn.setText("<")
        self._prev_btn.clicked.connect(self.previous_page)
        toolbar.addWidget(self._prev_btn)

        self._page_spin = QSpinBox()
        self._page_spin.setMinimum(1)
        self._page_spin.valueChanged.connect(lambda v: self.go_to_page(v - 1))
        toolbar.addWidget(self._page_spin)

        self._page_label = QLabel("/ 0")
        toolbar.addWidget(self._page_label)

        self._next_btn = QToolButton()
        self._next_btn.setText(">")
        self._next_btn.clicked.connect(self.next_page)
        toolbar.addWidget(self._next_btn)

        toolbar.addSeparator()

        # Zoom
        self._zoom_out_btn = QToolButton()
        self._zoom_out_btn.setText("-")
        self._zoom_out_btn.clicked.connect(self._view.zoom_out if hasattr(self, '_view') else lambda: None)
        toolbar.addWidget(self._zoom_out_btn)

        self._zoom_combo = QComboBox()
        self._zoom_combo.addItems(["50%", "75%", "100%", "125%", "150%", "200%", "Passend"])
        self._zoom_combo.setCurrentText("100%")
        self._zoom_combo.currentTextChanged.connect(self._on_zoom_changed)
        toolbar.addWidget(self._zoom_combo)

        self._zoom_in_btn = QToolButton()
        self._zoom_in_btn.setText("+")
        toolbar.addWidget(self._zoom_in_btn)

        toolbar.addSeparator()

        # Annotatie tools
        self._measure_btn = QToolButton()
        self._measure_btn.setText("📏 Meten")
        self._measure_btn.setCheckable(True)
        self._measure_btn.setToolTip("Afstanden meten op de tekening")
        self._measure_btn.toggled.connect(self._on_measure_toggled)
        toolbar.addWidget(self._measure_btn)

        self._annotate_btn = QToolButton()
        self._annotate_btn.setText("💬 Opmerking")
        self._annotate_btn.setCheckable(True)
        self._annotate_btn.setToolTip("Opmerkingen toevoegen aan de tekening")
        self._annotate_btn.toggled.connect(self._on_annotate_toggled)
        toolbar.addWidget(self._annotate_btn)

        self._clear_btn = QToolButton()
        self._clear_btn.setText("🗑️ Wis")
        self._clear_btn.setToolTip("Wis alle metingen en opmerkingen")
        self._clear_btn.clicked.connect(self._clear_all)
        toolbar.addWidget(self._clear_btn)

        toolbar.addSeparator()

        # Schaal instelling
        self._scale_label = QLabel("Schaal:")
        toolbar.addWidget(self._scale_label)

        self._scale_combo = QComboBox()
        self._scale_combo.addItems(["1:1", "1:10", "1:20", "1:50", "1:100", "1:200", "1:500"])
        self._scale_combo.setCurrentText("1:100")
        self._scale_combo.setToolTip("Tekeningschaal voor maatvoering")
        self._scale_combo.currentTextChanged.connect(self._on_scale_changed)
        toolbar.addWidget(self._scale_combo)

        layout.addWidget(toolbar)

        # Document view
        self._view = DocumentGraphicsView()
        self._zoom_in_btn.clicked.connect(self._view.zoom_in)
        self._zoom_out_btn.clicked.connect(self._view.zoom_out)
        layout.addWidget(self._view)

        # Measurement overlay (als kind van view)
        self._measurement_overlay = MeasurementOverlay(self._view.viewport())
        self._measurement_overlay.setGeometry(self._view.viewport().rect())

        # Stel standaard schaal in (1:100 bij 150 DPI)
        self._on_scale_changed("1:100")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, '_measurement_overlay'):
            self._measurement_overlay.setGeometry(self._view.viewport().rect())

    def open_file(self, file_path: str) -> bool:
        """Open een PDF bestand"""
        try:
            import fitz  # PyMuPDF
            self._fitz = fitz  # Sla module referentie op voor later gebruik

            self._doc = fitz.open(file_path)
            self._total_pages = len(self._doc)
            self._current_page = 0

            self._page_spin.setMaximum(self._total_pages)
            self._page_label.setText(f"/ {self._total_pages}")

            self._render_page()
            return True
        except ImportError:
            QMessageBox.warning(self, "PDF Viewer",
                                "PyMuPDF is niet geïnstalleerd.\nInstalleer met: pip install pymupdf")
            return False
        except Exception as e:
            QMessageBox.critical(self, "Fout", f"Kan PDF niet openen:\n{str(e)}")
            return False

    def _render_page(self):
        """Render de huidige pagina"""
        if not self._doc or not self._fitz or self._current_page >= self._total_pages:
            return

        page = self._doc[self._current_page]
        mat = self._fitz.Matrix(self._dpi / 72, self._dpi / 72)
        pix = page.get_pixmap(matrix=mat)

        # Convert to QPixmap
        img = QImage(pix.samples, pix.width, pix.height,
                     pix.stride, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(img)

        self._view.set_pixmap(pixmap)
        self._page_spin.setValue(self._current_page + 1)
        self.pageChanged.emit(self._current_page + 1, self._total_pages)

    def next_page(self):
        """Ga naar volgende pagina"""
        if self._current_page < self._total_pages - 1:
            self._current_page += 1
            self._render_page()

    def previous_page(self):
        """Ga naar vorige pagina"""
        if self._current_page > 0:
            self._current_page -= 1
            self._render_page()

    def go_to_page(self, page: int):
        """Ga naar specifieke pagina"""
        if 0 <= page < self._total_pages:
            self._current_page = page
            self._render_page()

    def _on_zoom_changed(self, text: str):
        """Verwerk zoom wijziging"""
        if text == "Passend":
            self._view.fit_in_view()
        else:
            try:
                scale = float(text.replace("%", "")) / 100
                self._view.set_zoom(scale)
            except ValueError:
                pass

    def set_measuring(self, enabled: bool):
        """Schakel maatvoering in/uit"""
        if enabled:
            self._measurement_overlay.start_measuring()
            self._view.setDragMode(QGraphicsView.NoDrag)
        else:
            self._measurement_overlay.stop_measuring()
            self._view.setDragMode(QGraphicsView.ScrollHandDrag)

    def set_scale(self, pixels_per_mm: float):
        """Stel de documentschaal in voor metingen"""
        self._measurement_overlay.set_scale(pixels_per_mm)

    def _on_measure_toggled(self, enabled: bool):
        """Schakel maatvoering modus in/uit"""
        if enabled:
            # Zet annotatie knop uit als meten aan gaat
            self._annotate_btn.setChecked(False)
        self.set_measuring(enabled)
        if enabled:
            # Zorg dat overlay muisgebeurtenissen ontvangt
            self._measurement_overlay.setAttribute(Qt.WA_TransparentForMouseEvents, False)
            self._measurement_overlay.raise_()
        elif not self._annotate_btn.isChecked():
            self._measurement_overlay.setAttribute(Qt.WA_TransparentForMouseEvents, True)

    def _on_annotate_toggled(self, enabled: bool):
        """Schakel annotatie modus in/uit"""
        if enabled:
            # Zet meten knop uit als annotatie aan gaat
            self._measure_btn.setChecked(False)
            self._measurement_overlay.start_annotating()
            self._measurement_overlay.setAttribute(Qt.WA_TransparentForMouseEvents, False)
            self._measurement_overlay.raise_()
            self._view.setDragMode(QGraphicsView.NoDrag)
        else:
            self._measurement_overlay.stop_annotating()
            if not self._measure_btn.isChecked():
                self._measurement_overlay.setAttribute(Qt.WA_TransparentForMouseEvents, True)
                self._view.setDragMode(QGraphicsView.ScrollHandDrag)

    def _clear_measurements(self):
        """Wis alle metingen"""
        self._measurement_overlay.clear_measurements()

    def _clear_all(self):
        """Wis alle metingen en opmerkingen"""
        self._measurement_overlay.clear_all()

    def _on_scale_changed(self, scale_text: str):
        """Verwerk schaal wijziging voor maatvoering"""
        # Parse schaal tekst (bijv. "1:100")
        try:
            parts = scale_text.split(":")
            if len(parts) == 2:
                scale_factor = float(parts[1]) / float(parts[0])
            else:
                scale_factor = 100  # default
        except (ValueError, ZeroDivisionError):
            scale_factor = 100

        # Bereken pixels per mm op basis van DPI en schaal
        # Bij 150 DPI: 150 pixels per inch = 150 / 25.4 pixels per mm
        # Bij schaal 1:100 betekent 1mm op tekening = 100mm werkelijk
        # Dus werkelijke mm = tekening_pixels / (dpi/25.4) * schaal_factor
        pixels_per_mm_on_paper = self._dpi / 25.4  # pixels per mm op papier
        pixels_per_real_mm = pixels_per_mm_on_paper / scale_factor  # pixels per werkelijke mm

        self._measurement_overlay.set_scale(pixels_per_real_mm)


class DXFViewer(QWidget):
    """DXF/DWG tekening viewer"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._doc = None

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        toolbar = QToolBar()

        # Layer selectie
        toolbar.addWidget(QLabel("Laag:"))
        self._layer_combo = QComboBox()
        self._layer_combo.addItem("Alle lagen")
        self._layer_combo.currentTextChanged.connect(self._on_layer_changed)
        toolbar.addWidget(self._layer_combo)

        toolbar.addSeparator()

        # Zoom
        self._zoom_out_btn = QToolButton()
        self._zoom_out_btn.setText("-")
        toolbar.addWidget(self._zoom_out_btn)

        self._zoom_fit_btn = QToolButton()
        self._zoom_fit_btn.setText("Passend")
        toolbar.addWidget(self._zoom_fit_btn)

        self._zoom_in_btn = QToolButton()
        self._zoom_in_btn.setText("+")
        toolbar.addWidget(self._zoom_in_btn)

        layout.addWidget(toolbar)

        # View
        self._view = DocumentGraphicsView()
        self._zoom_in_btn.clicked.connect(self._view.zoom_in)
        self._zoom_out_btn.clicked.connect(self._view.zoom_out)
        self._zoom_fit_btn.clicked.connect(self._view.fit_in_view)
        layout.addWidget(self._view)

        # Measurement overlay
        self._measurement_overlay = MeasurementOverlay(self._view.viewport())
        self._measurement_overlay.setGeometry(self._view.viewport().rect())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, '_measurement_overlay'):
            self._measurement_overlay.setGeometry(self._view.viewport().rect())

    def open_file(self, file_path: str) -> bool:
        """Open een DXF bestand"""
        try:
            import ezdxf

            self._doc = ezdxf.readfile(file_path)
            self._update_layers()
            self._render_drawing()
            return True
        except ImportError:
            QMessageBox.warning(self, "DXF Viewer",
                                "ezdxf is niet geïnstalleerd.\nInstalleer met: pip install ezdxf")
            return False
        except Exception as e:
            QMessageBox.critical(self, "Fout", f"Kan DXF niet openen:\n{str(e)}")
            return False

    def _update_layers(self):
        """Update de lagenlijst"""
        self._layer_combo.clear()
        self._layer_combo.addItem("Alle lagen")

        if self._doc:
            for layer in self._doc.layers:
                self._layer_combo.addItem(layer.dxf.name)

    def _render_drawing(self, layer_filter: str = None):
        """Render de DXF tekening naar een afbeelding"""
        if not self._doc:
            return

        try:
            from ezdxf.addons.drawing import Frontend, RenderContext
            from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
            import matplotlib.pyplot as plt
            from io import BytesIO

            # Maak matplotlib figuur
            fig, ax = plt.subplots(figsize=(16, 12), dpi=150)
            ax.set_aspect('equal')

            # Render DXF
            msp = self._doc.modelspace()
            ctx = RenderContext(self._doc)
            backend = MatplotlibBackend(ax)

            # Filter op laag indien nodig
            if layer_filter and layer_filter != "Alle lagen":
                entities = [e for e in msp if e.dxf.layer == layer_filter]
            else:
                entities = list(msp)

            Frontend(ctx, backend).draw_entities(entities)

            ax.axis('off')
            fig.tight_layout(pad=0)

            # Convert naar QPixmap
            buf = BytesIO()
            fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', pad_inches=0)
            buf.seek(0)
            plt.close(fig)

            img = QImage()
            img.loadFromData(buf.getvalue())
            pixmap = QPixmap.fromImage(img)

            self._view.set_pixmap(pixmap)

        except ImportError as e:
            # Fallback: toon bounding box info
            self._show_fallback_info()
        except Exception as e:
            QMessageBox.warning(self, "Render fout", f"Kan tekening niet renderen:\n{str(e)}")

    def _show_fallback_info(self):
        """Toon fallback informatie als matplotlib niet beschikbaar is"""
        if not self._doc:
            return

        msp = self._doc.modelspace()
        entity_count = len(list(msp))

        # Maak info pixmap
        pixmap = QPixmap(400, 300)
        pixmap.fill(Qt.white)

        painter = QPainter(pixmap)
        painter.setPen(Qt.black)
        font = QFont("Arial", 12)
        painter.setFont(font)

        y = 30
        painter.drawText(20, y, f"DXF Bestand geladen")
        y += 30
        painter.drawText(20, y, f"Entiteiten: {entity_count}")
        y += 30
        painter.drawText(20, y, f"Lagen: {len(self._doc.layers)}")
        y += 50
        painter.drawText(20, y, "Installeer matplotlib voor")
        y += 25
        painter.drawText(20, y, "volledige weergave:")
        y += 25
        painter.drawText(20, y, "pip install matplotlib")

        painter.end()

        self._view.set_pixmap(pixmap)

    def _on_layer_changed(self, layer: str):
        """Verwerk laag selectie"""
        self._render_drawing(layer if layer != "Alle lagen" else None)

    def set_measuring(self, enabled: bool):
        """Schakel maatvoering in/uit"""
        if enabled:
            self._measurement_overlay.start_measuring()
            self._view.setDragMode(QGraphicsView.NoDrag)
        else:
            self._measurement_overlay.stop_measuring()
            self._view.setDragMode(QGraphicsView.ScrollHandDrag)


class IFCViewer(QWidget):
    """IFC 3D model viewer (2D projectie)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = None

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        toolbar = QToolBar()

        # View selectie
        toolbar.addWidget(QLabel("Weergave:"))
        self._view_combo = QComboBox()
        self._view_combo.addItems(["Bovenaanzicht", "Vooraanzicht", "Rechts", "3D Iso"])
        self._view_combo.currentTextChanged.connect(self._on_view_changed)
        toolbar.addWidget(self._view_combo)

        toolbar.addSeparator()

        # Zoom
        self._zoom_out_btn = QToolButton()
        self._zoom_out_btn.setText("-")
        toolbar.addWidget(self._zoom_out_btn)

        self._zoom_fit_btn = QToolButton()
        self._zoom_fit_btn.setText("Passend")
        toolbar.addWidget(self._zoom_fit_btn)

        self._zoom_in_btn = QToolButton()
        self._zoom_in_btn.setText("+")
        toolbar.addWidget(self._zoom_in_btn)

        layout.addWidget(toolbar)

        # View
        self._view = DocumentGraphicsView()
        self._zoom_in_btn.clicked.connect(self._view.zoom_in)
        self._zoom_out_btn.clicked.connect(self._view.zoom_out)
        self._zoom_fit_btn.clicked.connect(self._view.fit_in_view)
        layout.addWidget(self._view)

        # Info label
        self._info_label = QLabel("Open een IFC bestand om te bekijken")
        self._info_label.setAlignment(Qt.AlignCenter)
        self._info_label.setStyleSheet("color: #666; font-size: 11pt;")

    def open_file(self, file_path: str) -> bool:
        """Open een IFC bestand"""
        try:
            import ifcopenshell
            import ifcopenshell.geom

            self._model = ifcopenshell.open(file_path)
            self._render_view()
            return True
        except ImportError:
            QMessageBox.warning(self, "IFC Viewer",
                                "ifcopenshell is niet correct geïnstalleerd.")
            return False
        except Exception as e:
            QMessageBox.critical(self, "Fout", f"Kan IFC niet openen:\n{str(e)}")
            return False

    def _render_view(self):
        """Render het IFC model"""
        if not self._model:
            return

        try:
            # Verzamel project info
            project = self._model.by_type("IfcProject")
            buildings = self._model.by_type("IfcBuilding")
            walls = self._model.by_type("IfcWall")
            slabs = self._model.by_type("IfcSlab")
            windows = self._model.by_type("IfcWindow")
            doors = self._model.by_type("IfcDoor")

            # Maak info weergave
            pixmap = QPixmap(500, 400)
            pixmap.fill(QColor(240, 240, 240))

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)

            # Header
            painter.setPen(QColor(41, 98, 255))
            font = QFont("Arial", 14, QFont.Bold)
            painter.setFont(font)
            painter.drawText(20, 35, "IFC Model Overzicht")

            # Lijn
            painter.setPen(QPen(QColor(41, 98, 255), 2))
            painter.drawLine(20, 45, 480, 45)

            # Info
            painter.setPen(Qt.black)
            font = QFont("Arial", 11)
            painter.setFont(font)

            y = 80
            line_height = 28

            if project:
                painter.drawText(30, y, f"Project: {project[0].Name or 'Onbekend'}")
                y += line_height

            if buildings:
                painter.drawText(30, y, f"Gebouw: {buildings[0].Name or 'Onbekend'}")
                y += line_height

            y += 10
            painter.drawText(30, y, f"Elementen:")
            y += line_height

            # Element tellingen
            painter.setPen(QColor(80, 80, 80))
            elements = [
                (f"Muren: {len(walls)}", walls),
                (f"Vloeren/Daken: {len(slabs)}", slabs),
                (f"Ramen: {len(windows)}", windows),
                (f"Deuren: {len(doors)}", doors),
            ]

            for text, items in elements:
                painter.drawText(50, y, text)
                y += 25

            # Hint
            y += 20
            painter.setPen(QColor(150, 150, 150))
            font = QFont("Arial", 9)
            painter.setFont(font)
            painter.drawText(30, y, "Tip: Gebruik Bonsai in Blender voor volledige 3D weergave")

            painter.end()

            self._view.set_pixmap(pixmap)

        except Exception as e:
            print(f"IFC render error: {e}")

    def _on_view_changed(self, view_type: str):
        """Verwerk view wijziging"""
        # In de toekomst: verschillende projecties renderen
        self._render_view()


class DocumentViewerPanel(QWidget):
    """Hoofd document viewer paneel met tabs voor meerdere documenten"""

    measurementRequested = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header met titel en knoppen
        header = QFrame()
        header.setFrameShape(QFrame.NoFrame)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f0f0f0, stop:1 #e0e0e0);
                border-bottom: 1px solid #ccc;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(8, 4, 8, 4)

        title = QLabel("Documenten")
        title.setStyleSheet("font-weight: bold; font-size: 10pt;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Open knop
        self._open_btn = QToolButton()
        self._open_btn.setText("+")
        self._open_btn.setToolTip("Document openen")
        self._open_btn.setFixedSize(24, 24)
        self._open_btn.setStyleSheet("""
            QToolButton {
                font-size: 14pt;
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 3px;
                background: #fff;
            }
            QToolButton:hover {
                background: #e0e0e0;
            }
        """)
        self._open_btn.clicked.connect(self._open_document)
        header_layout.addWidget(self._open_btn)

        layout.addWidget(header)

        # Tab widget voor documenten
        self._tabs = QTabWidget()
        self._tabs.setTabsClosable(True)
        self._tabs.tabCloseRequested.connect(self._close_tab)
        self._tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: #f5f5f5;
            }
            QTabBar::tab {
                background: #e0e0e0;
                border: 1px solid #ccc;
                border-bottom: none;
                padding: 6px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #f5f5f5;
                border-bottom: 1px solid #f5f5f5;
            }
        """)
        layout.addWidget(self._tabs)

        # Placeholder wanneer geen documenten open zijn
        self._placeholder = QLabel("Sleep documenten hierheen\nof klik + om te openen")
        self._placeholder.setAlignment(Qt.AlignCenter)
        self._placeholder.setStyleSheet("""
            color: #999;
            font-size: 11pt;
            padding: 40px;
        """)
        layout.addWidget(self._placeholder)

        self._update_placeholder()

    def _update_placeholder(self):
        """Update placeholder zichtbaarheid"""
        has_tabs = self._tabs.count() > 0
        self._tabs.setVisible(has_tabs)
        self._placeholder.setVisible(not has_tabs)

    def _open_document(self):
        """Open een document via dialoog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Document Openen",
            "",
            "Alle Ondersteunde (*.pdf *.ifc *.dxf *.dwg);;"
            "PDF Bestanden (*.pdf);;"
            "IFC Bestanden (*.ifc);;"
            "DXF/DWG Bestanden (*.dxf *.dwg);;"
            "Alle Bestanden (*.*)"
        )

        if file_path:
            self.open_file(file_path)

    def open_file(self, file_path: str) -> bool:
        """Open een bestand in de juiste viewer"""
        path = Path(file_path)
        suffix = path.suffix.lower()

        viewer = None
        if suffix == ".pdf":
            viewer = PDFViewer()
        elif suffix == ".ifc":
            # Gebruik de echte 3D viewer voor IFC bestanden
            global IFC3DViewer
            if IFC3DViewer is None:
                from .ifc_3d_viewer import IFC3DViewer as _IFC3DViewer
                IFC3DViewer = _IFC3DViewer
            viewer = IFC3DViewer()
        elif suffix in (".dxf", ".dwg"):
            viewer = DXFViewer()
        else:
            QMessageBox.warning(self, "Onbekend formaat",
                                f"Bestandsformaat '{suffix}' wordt niet ondersteund.")
            return False

        # IFC3DViewer gebruikt load_file i.p.v. open_file
        if suffix == ".ifc":
            viewer.load_file(file_path)
            index = self._tabs.addTab(viewer, f"🏗️ {path.name}")
            self._tabs.setCurrentIndex(index)
            self._update_placeholder()
            return True
        elif viewer.open_file(file_path):
            index = self._tabs.addTab(viewer, path.name)
            self._tabs.setCurrentIndex(index)
            self._update_placeholder()
            return True
        return False

    def open_pdf(self):
        """Open specifiek een PDF via dialoog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "PDF Openen", "", "PDF Bestanden (*.pdf)")
        if file_path:
            self.open_file(file_path)

    def open_pdf_file(self, file_path: str):
        """Open een PDF bestand direct via pad"""
        self.open_file(file_path)

    def open_ifc(self):
        """Open specifiek een IFC (2D info weergave)"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "IFC Openen", "", "IFC Bestanden (*.ifc)")
        if file_path:
            self.open_file(file_path)

    def open_ifc_3d(self):
        """Open specifiek een IFC in 3D viewer"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "IFC 3D Model Openen", "", "IFC Bestanden (*.ifc)")
        if file_path:
            self.open_file(file_path)

    def open_dxf(self):
        """Open specifiek een DXF/DWG"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "DXF/DWG Openen", "", "DXF/DWG Bestanden (*.dxf *.dwg)")
        if file_path:
            self.open_file(file_path)

    def _close_tab(self, index: int):
        """Sluit een document tab"""
        self._tabs.removeTab(index)
        self._update_placeholder()

    def set_measuring(self, enabled: bool):
        """Schakel maatvoering in/uit voor huidige viewer"""
        current = self._tabs.currentWidget()
        if current and hasattr(current, 'set_measuring'):
            current.set_measuring(enabled)

    def current_viewer(self):
        """Geef de huidige viewer terug"""
        return self._tabs.currentWidget()
