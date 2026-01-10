"""
Icons - 3D-stijl iconen genereren voor de ribbon toolbar
"""

from PySide6.QtGui import QIcon, QPixmap, QImage, QPainter, QColor, QLinearGradient, QPen, QBrush, QFont, QPainterPath
from PySide6.QtCore import Qt, QRect, QRectF, QPointF
import math


def create_gradient_icon(size: int, colors: tuple, shape: str = "rect") -> QPixmap:
    """Maak een basis icoon met gradient"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Gradient
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor(*colors[0]))
    gradient.setColorAt(1, QColor(*colors[1]))

    margin = size // 8
    rect = QRectF(margin, margin, size - 2*margin, size - 2*margin)

    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(*colors[1]), 1))

    if shape == "rect":
        painter.drawRoundedRect(rect, 4, 4)
    elif shape == "circle":
        painter.drawEllipse(rect)

    painter.end()
    return pixmap


def create_3d_document_icon(size: int = 32) -> QIcon:
    """Maak een 3D document icoon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Document met schaduw effect
    shadow_offset = 2
    margin = 4

    # Schaduw
    painter.setBrush(QColor(0, 0, 0, 50))
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(margin + shadow_offset, margin + shadow_offset,
                            size - 2*margin, size - 2*margin, 2, 2)

    # Document achtergrond
    gradient = QLinearGradient(margin, margin, size - margin, size - margin)
    gradient.setColorAt(0, QColor(255, 255, 255))
    gradient.setColorAt(1, QColor(230, 230, 230))

    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(180, 180, 180), 1))
    painter.drawRoundedRect(margin, margin, size - 2*margin - shadow_offset,
                            size - 2*margin - shadow_offset, 2, 2)

    # Lijnen op document
    painter.setPen(QPen(QColor(200, 200, 200), 1))
    line_start = margin + 4
    line_end = size - margin - shadow_offset - 4
    for i in range(3):
        y = margin + 8 + i * 5
        painter.drawLine(line_start, y, line_end, y)

    painter.end()
    return QIcon(pixmap)


def create_3d_folder_icon(size: int = 32) -> QIcon:
    """Maak een 3D map icoon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    margin = 3

    # Map achterkant
    gradient_back = QLinearGradient(0, 0, 0, size)
    gradient_back.setColorAt(0, QColor(255, 193, 7))
    gradient_back.setColorAt(1, QColor(255, 152, 0))

    painter.setBrush(QBrush(gradient_back))
    painter.setPen(QPen(QColor(245, 127, 23), 1))

    path = QPainterPath()
    path.moveTo(margin, margin + 6)
    path.lineTo(margin + 8, margin + 6)
    path.lineTo(margin + 10, margin + 2)
    path.lineTo(size - margin, margin + 2)
    path.lineTo(size - margin, size - margin - 2)
    path.lineTo(margin, size - margin - 2)
    path.closeSubpath()
    painter.drawPath(path)

    # Map voorkant
    gradient_front = QLinearGradient(0, size//2, 0, size)
    gradient_front.setColorAt(0, QColor(255, 213, 79))
    gradient_front.setColorAt(1, QColor(255, 183, 77))

    painter.setBrush(QBrush(gradient_front))
    painter.drawRoundedRect(margin, margin + 8, size - 2*margin, size - margin - 10, 2, 2)

    painter.end()
    return QIcon(pixmap)


def create_3d_save_icon(size: int = 32) -> QIcon:
    """Maak een 3D opslaan icoon (diskette)"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    margin = 4

    # Diskette body
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor(66, 165, 245))
    gradient.setColorAt(1, QColor(30, 136, 229))

    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(21, 101, 192), 1))
    painter.drawRoundedRect(margin, margin, size - 2*margin, size - 2*margin, 3, 3)

    # Label
    painter.setBrush(QColor(255, 255, 255))
    painter.setPen(Qt.NoPen)
    label_margin = margin + 4
    painter.drawRect(label_margin, size//2, size - 2*label_margin, size//2 - margin - 2)

    # Metalen schuif
    painter.setBrush(QColor(180, 180, 180))
    slider_w = 8
    painter.drawRect(size//2 - slider_w//2, margin + 2, slider_w, 8)

    painter.end()
    return QIcon(pixmap)


def create_3d_print_icon(size: int = 32) -> QIcon:
    """Maak een 3D print icoon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    margin = 3

    # Printer body
    gradient = QLinearGradient(0, 0, 0, size)
    gradient.setColorAt(0, QColor(120, 120, 120))
    gradient.setColorAt(1, QColor(80, 80, 80))

    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(60, 60, 60), 1))
    painter.drawRoundedRect(margin, size//3, size - 2*margin, size//2, 3, 3)

    # Papier invoer
    painter.setBrush(QColor(255, 255, 255))
    painter.setPen(QPen(QColor(200, 200, 200), 1))
    paper_margin = margin + 6
    painter.drawRect(paper_margin, margin, size - 2*paper_margin, size//3)

    # Papier uitvoer
    painter.drawRect(paper_margin, size - margin - 6, size - 2*paper_margin, 8)

    painter.end()
    return QIcon(pixmap)


def create_3d_cut_icon(size: int = 32) -> QIcon:
    """Maak een 3D schaar icoon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Schaar bladen
    painter.setPen(QPen(QColor(100, 100, 100), 3, Qt.SolidLine, Qt.RoundCap))

    center = size // 2

    # Linker blad
    painter.drawLine(center - 2, center, 4, 4)
    # Rechter blad
    painter.drawLine(center + 2, center, size - 4, 4)

    # Handvatten
    gradient = QLinearGradient(0, center, 0, size)
    gradient.setColorAt(0, QColor(244, 67, 54))
    gradient.setColorAt(1, QColor(211, 47, 47))

    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(183, 28, 28), 1))

    # Linker handvat
    painter.drawEllipse(2, size - 12, 10, 10)
    # Rechter handvat
    painter.drawEllipse(size - 12, size - 12, 10, 10)

    # Verbindingspunt
    painter.setBrush(QColor(150, 150, 150))
    painter.drawEllipse(center - 3, center - 3, 6, 6)

    painter.end()
    return QIcon(pixmap)


def create_3d_copy_icon(size: int = 32) -> QIcon:
    """Maak een 3D kopieer icoon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Achterste document
    gradient1 = QLinearGradient(8, 8, 24, 24)
    gradient1.setColorAt(0, QColor(200, 200, 200))
    gradient1.setColorAt(1, QColor(160, 160, 160))

    painter.setBrush(QBrush(gradient1))
    painter.setPen(QPen(QColor(120, 120, 120), 1))
    painter.drawRoundedRect(8, 2, size - 12, size - 12, 2, 2)

    # Voorste document
    gradient2 = QLinearGradient(2, 8, 20, 28)
    gradient2.setColorAt(0, QColor(255, 255, 255))
    gradient2.setColorAt(1, QColor(240, 240, 240))

    painter.setBrush(QBrush(gradient2))
    painter.setPen(QPen(QColor(180, 180, 180), 1))
    painter.drawRoundedRect(2, 8, size - 12, size - 12, 2, 2)

    # Lijnen
    painter.setPen(QPen(QColor(200, 200, 200), 1))
    for i in range(3):
        y = 14 + i * 5
        painter.drawLine(6, y, size - 16, y)

    painter.end()
    return QIcon(pixmap)


def create_3d_paste_icon(size: int = 32) -> QIcon:
    """Maak een 3D plakken icoon (klembord)"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    margin = 4

    # Klembord
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor(161, 136, 127))
    gradient.setColorAt(1, QColor(121, 85, 72))

    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(93, 64, 55), 1))
    painter.drawRoundedRect(margin, margin + 4, size - 2*margin, size - margin - 6, 3, 3)

    # Clip
    painter.setBrush(QColor(150, 150, 150))
    painter.setPen(QPen(QColor(100, 100, 100), 1))
    clip_w = 12
    painter.drawRoundedRect(size//2 - clip_w//2, margin, clip_w, 8, 2, 2)

    # Papier
    painter.setBrush(QColor(255, 255, 255))
    painter.setPen(QPen(QColor(200, 200, 200), 1))
    painter.drawRect(margin + 4, margin + 10, size - 2*margin - 8, size - margin - 18)

    painter.end()
    return QIcon(pixmap)


def create_3d_chapter_icon(size: int = 32) -> QIcon:
    """Maak een 3D hoofdstuk icoon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Boek
    gradient = QLinearGradient(0, 0, size, 0)
    gradient.setColorAt(0, QColor(103, 58, 183))
    gradient.setColorAt(0.5, QColor(126, 87, 194))
    gradient.setColorAt(1, QColor(103, 58, 183))

    margin = 4
    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(69, 39, 160), 1))
    painter.drawRoundedRect(margin, margin, size - 2*margin, size - 2*margin, 2, 2)

    # Pagina's
    painter.setBrush(QColor(255, 255, 255))
    painter.setPen(Qt.NoPen)
    painter.drawRect(margin + 3, margin + 2, size - 2*margin - 6, size - 2*margin - 4)

    # Lijnen
    painter.setPen(QPen(QColor(200, 200, 200), 1))
    for i in range(4):
        y = margin + 6 + i * 5
        painter.drawLine(margin + 6, y, size - margin - 6, y)

    painter.end()
    return QIcon(pixmap)


def create_3d_cost_item_icon(size: int = 32) -> QIcon:
    """Maak een 3D kostenpost icoon (euro)"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Cirkel achtergrond
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor(76, 175, 80))
    gradient.setColorAt(1, QColor(56, 142, 60))

    margin = 3
    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(46, 125, 50), 2))
    painter.drawEllipse(margin, margin, size - 2*margin, size - 2*margin)

    # Euro teken
    painter.setPen(QPen(QColor(255, 255, 255), 3))
    font = QFont("Arial", size // 2, QFont.Bold)
    painter.setFont(font)
    painter.drawText(QRect(0, 0, size, size), Qt.AlignCenter, "€")

    painter.end()
    return QIcon(pixmap)


def create_3d_text_row_icon(size: int = 32) -> QIcon:
    """Maak een 3D tekstregel icoon (T in vierkant)"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Vierkante achtergrond
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor(156, 163, 175))  # Grijs
    gradient.setColorAt(1, QColor(107, 114, 128))

    margin = 3
    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(75, 85, 99), 2))
    painter.drawRoundedRect(margin, margin, size - 2*margin, size - 2*margin, 4, 4)

    # "T" letter voor tekst
    painter.setPen(QPen(QColor(255, 255, 255), 3))
    font = QFont("Arial", size // 2, QFont.Bold)
    painter.setFont(font)
    painter.drawText(QRect(0, 0, size, size), Qt.AlignCenter, "T")

    painter.end()
    return QIcon(pixmap)


def create_3d_delete_icon(size: int = 32) -> QIcon:
    """Maak een 3D verwijder icoon (prullenbak)"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    margin = 4

    # Prullenbak body
    gradient = QLinearGradient(0, 0, 0, size)
    gradient.setColorAt(0, QColor(239, 83, 80))
    gradient.setColorAt(1, QColor(211, 47, 47))

    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(183, 28, 28), 1))

    # Bak
    path = QPainterPath()
    path.moveTo(margin + 2, margin + 8)
    path.lineTo(margin + 4, size - margin)
    path.lineTo(size - margin - 4, size - margin)
    path.lineTo(size - margin - 2, margin + 8)
    path.closeSubpath()
    painter.drawPath(path)

    # Deksel
    painter.drawRoundedRect(margin, margin + 4, size - 2*margin, 4, 1, 1)

    # Handvat
    painter.setBrush(Qt.NoBrush)
    painter.drawRoundedRect(size//2 - 4, margin, 8, 4, 1, 1)

    # Lijnen
    painter.setPen(QPen(QColor(255, 255, 255, 150), 1))
    for x in [size//3, size//2, 2*size//3]:
        painter.drawLine(x, margin + 12, x, size - margin - 3)

    painter.end()
    return QIcon(pixmap)


def create_3d_pdf_icon(size: int = 32) -> QIcon:
    """Maak een 3D PDF icoon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    margin = 3

    # Document
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor(244, 67, 54))
    gradient.setColorAt(1, QColor(211, 47, 47))

    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(183, 28, 28), 1))
    painter.drawRoundedRect(margin, margin, size - 2*margin, size - 2*margin, 3, 3)

    # PDF tekst
    painter.setPen(QColor(255, 255, 255))
    font = QFont("Arial", 7, QFont.Bold)
    painter.setFont(font)
    painter.drawText(QRect(0, 0, size, size), Qt.AlignCenter, "PDF")

    painter.end()
    return QIcon(pixmap)


def create_3d_ifc_icon(size: int = 32) -> QIcon:
    """Maak een 3D IFC icoon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    margin = 3

    # 3D kubus effect
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor(0, 150, 136))
    gradient.setColorAt(1, QColor(0, 121, 107))

    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(0, 105, 92), 1))

    # Kubus bovenkant
    path_top = QPainterPath()
    path_top.moveTo(size//2, margin)
    path_top.lineTo(size - margin, margin + 8)
    path_top.lineTo(size//2, margin + 16)
    path_top.lineTo(margin, margin + 8)
    path_top.closeSubpath()

    painter.setBrush(QColor(0, 188, 170))
    painter.drawPath(path_top)

    # Kubus linkerkant
    path_left = QPainterPath()
    path_left.moveTo(margin, margin + 8)
    path_left.lineTo(size//2, margin + 16)
    path_left.lineTo(size//2, size - margin)
    path_left.lineTo(margin, size - margin - 8)
    path_left.closeSubpath()

    painter.setBrush(QColor(0, 150, 136))
    painter.drawPath(path_left)

    # Kubus rechterkant
    path_right = QPainterPath()
    path_right.moveTo(size - margin, margin + 8)
    path_right.lineTo(size//2, margin + 16)
    path_right.lineTo(size//2, size - margin)
    path_right.lineTo(size - margin, size - margin - 8)
    path_right.closeSubpath()

    painter.setBrush(QColor(0, 121, 107))
    painter.drawPath(path_right)

    painter.end()
    return QIcon(pixmap)


def create_3d_dxf_icon(size: int = 32) -> QIcon:
    """Maak een 3D DXF icoon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    margin = 3

    # Document
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor(255, 152, 0))
    gradient.setColorAt(1, QColor(245, 124, 0))

    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(230, 81, 0), 1))
    painter.drawRoundedRect(margin, margin, size - 2*margin, size - 2*margin, 3, 3)

    # Technische lijnen
    painter.setPen(QPen(QColor(255, 255, 255), 1))
    painter.drawLine(margin + 6, size//2, size - margin - 6, size//3)
    painter.drawLine(margin + 6, size//2, size//2, size - margin - 6)
    painter.drawLine(size//2, size - margin - 6, size - margin - 6, size//2)

    painter.end()
    return QIcon(pixmap)


def create_3d_measure_icon(size: int = 32) -> QIcon:
    """Maak een 3D meetlint icoon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Meetlint
    gradient = QLinearGradient(0, 0, size, 0)
    gradient.setColorAt(0, QColor(255, 235, 59))
    gradient.setColorAt(1, QColor(255, 193, 7))

    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(245, 127, 23), 1))

    # Diagonaal lint
    painter.save()
    painter.translate(size//2, size//2)
    painter.rotate(-30)
    painter.drawRoundedRect(-size//2 + 2, -4, size - 4, 10, 2, 2)

    # Streepjes
    painter.setPen(QPen(QColor(0, 0, 0), 1))
    for i in range(-size//2 + 6, size//2 - 4, 4):
        h = 3 if i % 8 == 0 else 2
        painter.drawLine(i, -4, i, -4 + h)

    painter.restore()

    painter.end()
    return QIcon(pixmap)


def create_3d_zoom_in_icon(size: int = 32) -> QIcon:
    """Maak een 3D zoom in icoon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Vergrootglas
    gradient = QLinearGradient(4, 4, 20, 20)
    gradient.setColorAt(0, QColor(227, 242, 253))
    gradient.setColorAt(1, QColor(187, 222, 251))

    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(30, 136, 229), 2))
    painter.drawEllipse(4, 4, 18, 18)

    # Handvat
    painter.setPen(QPen(QColor(100, 100, 100), 3, Qt.SolidLine, Qt.RoundCap))
    painter.drawLine(19, 19, size - 4, size - 4)

    # Plus
    painter.setPen(QPen(QColor(30, 136, 229), 2))
    painter.drawLine(9, 13, 17, 13)
    painter.drawLine(13, 9, 13, 17)

    painter.end()
    return QIcon(pixmap)


def create_3d_zoom_out_icon(size: int = 32) -> QIcon:
    """Maak een 3D zoom uit icoon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Vergrootglas
    gradient = QLinearGradient(4, 4, 20, 20)
    gradient.setColorAt(0, QColor(227, 242, 253))
    gradient.setColorAt(1, QColor(187, 222, 251))

    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(30, 136, 229), 2))
    painter.drawEllipse(4, 4, 18, 18)

    # Handvat
    painter.setPen(QPen(QColor(100, 100, 100), 3, Qt.SolidLine, Qt.RoundCap))
    painter.drawLine(19, 19, size - 4, size - 4)

    # Min
    painter.setPen(QPen(QColor(30, 136, 229), 2))
    painter.drawLine(9, 13, 17, 13)

    painter.end()
    return QIcon(pixmap)


def create_3d_fit_icon(size: int = 32) -> QIcon:
    """Maak een 3D passend maken icoon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    painter.setPen(QPen(QColor(66, 165, 245), 2))

    margin = 4
    corner_len = 8

    # Linker boven hoek
    painter.drawLine(margin, margin, margin + corner_len, margin)
    painter.drawLine(margin, margin, margin, margin + corner_len)

    # Rechter boven hoek
    painter.drawLine(size - margin, margin, size - margin - corner_len, margin)
    painter.drawLine(size - margin, margin, size - margin, margin + corner_len)

    # Linker onder hoek
    painter.drawLine(margin, size - margin, margin + corner_len, size - margin)
    painter.drawLine(margin, size - margin, margin, size - margin - corner_len)

    # Rechter onder hoek
    painter.drawLine(size - margin, size - margin, size - margin - corner_len, size - margin)
    painter.drawLine(size - margin, size - margin, size - margin, size - margin - corner_len)

    # Pijlen naar binnen
    center = size // 2
    arrow_len = 4

    painter.setPen(QPen(QColor(66, 165, 245), 1))
    # Naar rechts
    painter.drawLine(margin + 2, center, margin + 6, center)
    # Naar links
    painter.drawLine(size - margin - 2, center, size - margin - 6, center)
    # Naar beneden
    painter.drawLine(center, margin + 2, center, margin + 6)
    # Naar boven
    painter.drawLine(center, size - margin - 2, center, size - margin - 6)

    painter.end()
    return QIcon(pixmap)



def create_3d_excel_icon(size: int = 32) -> QIcon:
    """Maak een 3D Excel icoon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    margin = 3

    # Groene achtergrond
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor(33, 115, 70))
    gradient.setColorAt(1, QColor(24, 90, 55))

    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(20, 70, 45), 1))
    painter.drawRoundedRect(margin, margin, size - 2*margin, size - 2*margin, 3, 3)

    # X letter
    painter.setPen(QPen(QColor(255, 255, 255), 2))
    font = QFont("Arial", size // 3, QFont.Bold)
    painter.setFont(font)
    painter.drawText(QRect(0, 0, size, size), Qt.AlignCenter, "X")

    painter.end()
    return QIcon(pixmap)


def create_3d_ods_icon(size: int = 32) -> QIcon:
    """Maak een 3D ODS icoon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    margin = 3

    # Oranje achtergrond
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor(232, 110, 0))
    gradient.setColorAt(1, QColor(200, 90, 0))

    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(180, 80, 0), 1))
    painter.drawRoundedRect(margin, margin, size - 2*margin, size - 2*margin, 3, 3)

    # ODS tekst
    painter.setPen(QPen(QColor(255, 255, 255), 1))
    font = QFont("Arial", size // 4, QFont.Bold)
    painter.setFont(font)
    painter.drawText(QRect(0, 0, size, size), Qt.AlignCenter, "ODS")

    painter.end()
    return QIcon(pixmap)


def create_3d_csv_icon(size: int = 32) -> QIcon:
    """Maak een 3D CSV icoon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    margin = 3

    # Blauwe achtergrond
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor(63, 81, 181))
    gradient.setColorAt(1, QColor(48, 63, 159))

    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(40, 53, 147), 1))
    painter.drawRoundedRect(margin, margin, size - 2*margin, size - 2*margin, 3, 3)

    # CSV tekst
    painter.setPen(QPen(QColor(255, 255, 255), 1))
    font = QFont("Arial", size // 4, QFont.Bold)
    painter.setFont(font)
    painter.drawText(QRect(0, 0, size, size), Qt.AlignCenter, "CSV")

    painter.end()
    return QIcon(pixmap)


def create_3d_up_icon(size: int = 32) -> QIcon:
    """Maak een 3D omhoog pijl icoon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    center = size // 2

    # Pijl
    gradient = QLinearGradient(0, size, 0, 0)
    gradient.setColorAt(0, QColor(33, 150, 243))
    gradient.setColorAt(1, QColor(100, 181, 246))

    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(21, 101, 192), 1))

    path = QPainterPath()
    path.moveTo(center, 4)
    path.lineTo(size - 6, center + 2)
    path.lineTo(center + 4, center + 2)
    path.lineTo(center + 4, size - 4)
    path.lineTo(center - 4, size - 4)
    path.lineTo(center - 4, center + 2)
    path.lineTo(6, center + 2)
    path.closeSubpath()

    painter.drawPath(path)

    painter.end()
    return QIcon(pixmap)


def create_3d_down_icon(size: int = 32) -> QIcon:
    """Maak een 3D omlaag pijl icoon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    center = size // 2

    # Pijl
    gradient = QLinearGradient(0, 0, 0, size)
    gradient.setColorAt(0, QColor(100, 181, 246))
    gradient.setColorAt(1, QColor(33, 150, 243))

    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(21, 101, 192), 1))

    path = QPainterPath()
    path.moveTo(center, size - 4)
    path.lineTo(size - 6, center - 2)
    path.lineTo(center + 4, center - 2)
    path.lineTo(center + 4, 4)
    path.lineTo(center - 4, 4)
    path.lineTo(center - 4, center - 2)
    path.lineTo(6, center - 2)
    path.closeSubpath()

    painter.drawPath(path)

    painter.end()
    return QIcon(pixmap)


def create_3d_indent_in_icon(size: int = 32) -> QIcon:
    """Maak een 3D inspringen icoon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Lijnen
    painter.setPen(QPen(QColor(100, 100, 100), 2))
    y_start = 6
    for i in range(4):
        y = y_start + i * 6
        x_start = 8 if i > 0 else 4
        painter.drawLine(x_start, y, size - 4, y)

    # Pijl naar rechts
    gradient = QLinearGradient(0, 0, size // 2, 0)
    gradient.setColorAt(0, QColor(76, 175, 80))
    gradient.setColorAt(1, QColor(129, 199, 132))

    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(56, 142, 60), 1))

    path = QPainterPath()
    center_y = size // 2 + 4
    path.moveTo(4, center_y - 4)
    path.lineTo(12, center_y)
    path.lineTo(4, center_y + 4)
    path.closeSubpath()

    painter.drawPath(path)

    painter.end()
    return QIcon(pixmap)


def create_3d_indent_out_icon(size: int = 32) -> QIcon:
    """Maak een 3D uitspringen icoon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Lijnen
    painter.setPen(QPen(QColor(100, 100, 100), 2))
    y_start = 6
    for i in range(4):
        y = y_start + i * 6
        x_start = 4 if i > 0 else 8
        painter.drawLine(x_start, y, size - 4, y)

    # Pijl naar links
    gradient = QLinearGradient(size // 2, 0, 0, 0)
    gradient.setColorAt(0, QColor(255, 152, 0))
    gradient.setColorAt(1, QColor(255, 183, 77))

    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(245, 124, 0), 1))

    path = QPainterPath()
    center_y = size // 2 + 4
    path.moveTo(12, center_y - 4)
    path.lineTo(4, center_y)
    path.lineTo(12, center_y + 4)
    path.closeSubpath()

    painter.drawPath(path)

    painter.end()
    return QIcon(pixmap)


def create_3d_calculator_icon(size: int = 32) -> QIcon:
    """Maak een 3D calculator icoon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    margin = 3

    # Calculator body
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor(66, 66, 66))
    gradient.setColorAt(1, QColor(33, 33, 33))

    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(20, 20, 20), 1))
    painter.drawRoundedRect(margin, margin, size - 2*margin, size - 2*margin, 3, 3)

    # Display
    painter.setBrush(QColor(200, 230, 200))
    painter.setPen(Qt.NoPen)
    painter.drawRect(margin + 3, margin + 3, size - 2*margin - 6, size // 4)

    # Knoppen (3x4 grid)
    button_size = (size - 2*margin - 8) // 3
    button_y_start = margin + 3 + size // 4 + 2

    painter.setBrush(QColor(100, 100, 100))
    for row in range(3):
        for col in range(3):
            x = margin + 3 + col * (button_size + 1)
            y = button_y_start + row * (button_size + 1)
            painter.drawRect(x, y, button_size - 1, button_size - 1)

    painter.end()
    return QIcon(pixmap)


def create_3d_expand_icon(size: int = 32) -> QIcon:
    """Maak een expand/uitklappen icoon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    margin = size // 6
    center = size // 2

    # Achtergrond cirkel
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor(34, 197, 94))  # Groen
    gradient.setColorAt(1, QColor(22, 163, 74))

    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(21, 128, 61), 1))
    painter.drawEllipse(margin, margin, size - 2*margin, size - 2*margin)

    # Plus/expand symbool (pijlen naar buiten)
    painter.setPen(QPen(QColor(255, 255, 255), max(2, size // 10)))

    # Horizontale pijlen
    arrow_size = size // 5
    painter.drawLine(margin + 4, center, center - 2, center)
    painter.drawLine(center + 2, center, size - margin - 4, center)

    # Verticale pijlen
    painter.drawLine(center, margin + 4, center, center - 2)
    painter.drawLine(center, center + 2, center, size - margin - 4)

    painter.end()
    return QIcon(pixmap)


def create_3d_collapse_icon(size: int = 32) -> QIcon:
    """Maak een collapse/inklappen icoon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    margin = size // 6
    center = size // 2

    # Achtergrond cirkel
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor(249, 115, 22))  # Oranje
    gradient.setColorAt(1, QColor(234, 88, 12))

    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(194, 65, 12), 1))
    painter.drawEllipse(margin, margin, size - 2*margin, size - 2*margin)

    # Minus symbool (horizontale lijn)
    painter.setPen(QPen(QColor(255, 255, 255), max(2, size // 8)))
    painter.drawLine(margin + 6, center, size - margin - 6, center)

    painter.end()
    return QIcon(pixmap)


def create_3d_bold_icon(size: int = 32) -> QIcon:
    """Maak een vet (bold) icoon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Achtergrond
    painter.setBrush(QColor(240, 240, 240))
    painter.setPen(QPen(QColor(180, 180, 180), 1))
    painter.drawRoundedRect(2, 2, size - 4, size - 4, 4, 4)

    # B letter
    painter.setPen(QColor(50, 50, 50))
    font = QFont("Arial", size // 2, QFont.Bold)
    painter.setFont(font)
    painter.drawText(QRect(0, 0, size, size), Qt.AlignCenter, "B")

    painter.end()
    return QIcon(pixmap)


def create_3d_italic_icon(size: int = 32) -> QIcon:
    """Maak een cursief (italic) icoon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Achtergrond
    painter.setBrush(QColor(240, 240, 240))
    painter.setPen(QPen(QColor(180, 180, 180), 1))
    painter.drawRoundedRect(2, 2, size - 4, size - 4, 4, 4)

    # I letter (cursief)
    painter.setPen(QColor(50, 50, 50))
    font = QFont("Arial", size // 2)
    font.setItalic(True)
    painter.setFont(font)
    painter.drawText(QRect(0, 0, size, size), Qt.AlignCenter, "I")

    painter.end()
    return QIcon(pixmap)


def create_3d_underline_icon(size: int = 32) -> QIcon:
    """Maak een onderstrepen icoon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Achtergrond
    painter.setBrush(QColor(240, 240, 240))
    painter.setPen(QPen(QColor(180, 180, 180), 1))
    painter.drawRoundedRect(2, 2, size - 4, size - 4, 4, 4)

    # U letter
    painter.setPen(QColor(50, 50, 50))
    font = QFont("Arial", size // 2)
    painter.setFont(font)
    painter.drawText(QRect(0, -2, size, size), Qt.AlignCenter, "U")

    # Onderstreep lijn
    painter.setPen(QPen(QColor(50, 50, 50), 2))
    painter.drawLine(size // 4, size - 6, size - size // 4, size - 6)

    painter.end()
    return QIcon(pixmap)


def create_3d_color_icon(size: int = 32) -> QIcon:
    """Maak een tekstkleur icoon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Achtergrond
    painter.setBrush(QColor(240, 240, 240))
    painter.setPen(QPen(QColor(180, 180, 180), 1))
    painter.drawRoundedRect(2, 2, size - 4, size - 4, 4, 4)

    # A letter
    painter.setPen(QColor(50, 50, 50))
    font = QFont("Arial", size // 2, QFont.Bold)
    painter.setFont(font)
    painter.drawText(QRect(0, -2, size, size), Qt.AlignCenter, "A")

    # Kleur balk onderaan
    painter.setBrush(QColor(231, 76, 60))  # Rood
    painter.setPen(Qt.NoPen)
    painter.drawRect(4, size - 8, size - 8, 4)

    painter.end()
    return QIcon(pixmap)


def create_3d_odt_icon(size: int = 32) -> QIcon:
    """Maak een 3D ODT icoon"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    margin = 3

    # Blauwe achtergrond (LibreOffice Writer)
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor(0, 102, 204))
    gradient.setColorAt(1, QColor(0, 76, 153))

    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(0, 60, 120), 1))
    painter.drawRoundedRect(margin, margin, size - 2*margin, size - 2*margin, 3, 3)

    # ODT tekst
    painter.setPen(QPen(QColor(255, 255, 255), 1))
    font = QFont("Arial", size // 4, QFont.Bold)
    painter.setFont(font)
    painter.drawText(QRect(0, 0, size, size), Qt.AlignCenter, "ODT")

    painter.end()
    return QIcon(pixmap)


def create_3d_undo_icon(size: int = 32) -> QIcon:
    """Maak een 3D ongedaan maken icoon (gebogen pijl naar links)"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    center = size // 2
    margin = 4

    # Gebogen pijl naar links
    gradient = QLinearGradient(0, 0, size, 0)
    gradient.setColorAt(0, QColor(66, 165, 245))
    gradient.setColorAt(1, QColor(30, 136, 229))

    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(21, 101, 192), 2))

    # Boog tekenen
    path = QPainterPath()
    path.moveTo(margin + 6, center - 2)
    path.arcTo(margin + 4, margin + 4, size - 2*margin - 8, size - 2*margin - 4, 180, -180)

    painter.setBrush(Qt.NoBrush)
    painter.drawPath(path)

    # Pijlpunt
    painter.setBrush(QBrush(gradient))
    arrow_path = QPainterPath()
    arrow_path.moveTo(margin + 2, center - 2)
    arrow_path.lineTo(margin + 10, center - 8)
    arrow_path.lineTo(margin + 10, center + 4)
    arrow_path.closeSubpath()
    painter.drawPath(arrow_path)

    painter.end()
    return QIcon(pixmap)


def create_3d_redo_icon(size: int = 32) -> QIcon:
    """Maak een 3D opnieuw icoon (gebogen pijl naar rechts)"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    center = size // 2
    margin = 4

    # Gebogen pijl naar rechts
    gradient = QLinearGradient(size, 0, 0, 0)
    gradient.setColorAt(0, QColor(102, 187, 106))
    gradient.setColorAt(1, QColor(67, 160, 71))

    painter.setBrush(QBrush(gradient))
    painter.setPen(QPen(QColor(46, 125, 50), 2))

    # Boog tekenen
    path = QPainterPath()
    path.moveTo(size - margin - 6, center - 2)
    path.arcTo(margin + 4, margin + 4, size - 2*margin - 8, size - 2*margin - 4, 0, 180)

    painter.setBrush(Qt.NoBrush)
    painter.drawPath(path)

    # Pijlpunt
    painter.setBrush(QBrush(gradient))
    arrow_path = QPainterPath()
    arrow_path.moveTo(size - margin - 2, center - 2)
    arrow_path.lineTo(size - margin - 10, center - 8)
    arrow_path.lineTo(size - margin - 10, center + 4)
    arrow_path.closeSubpath()
    painter.drawPath(arrow_path)

    painter.end()
    return QIcon(pixmap)


def create_tree_expand_icon(size: int = 16) -> QPixmap:
    """Maak een + icoon voor tree expand"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    margin = 2
    box_size = size - 2 * margin

    # Vierkant met border
    painter.setBrush(QColor(255, 255, 255))
    painter.setPen(QPen(QColor(130, 130, 130), 1))
    painter.drawRect(margin, margin, box_size, box_size)

    # Plus teken
    painter.setPen(QPen(QColor(80, 80, 80), 2))
    center = size // 2
    line_margin = 4
    painter.drawLine(line_margin, center, size - line_margin, center)  # Horizontaal
    painter.drawLine(center, line_margin, center, size - line_margin)  # Verticaal

    painter.end()
    return pixmap


def create_tree_collapse_icon(size: int = 16) -> QPixmap:
    """Maak een - icoon voor tree collapse"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    margin = 2
    box_size = size - 2 * margin

    # Vierkant met border
    painter.setBrush(QColor(255, 255, 255))
    painter.setPen(QPen(QColor(130, 130, 130), 1))
    painter.drawRect(margin, margin, box_size, box_size)

    # Min teken
    painter.setPen(QPen(QColor(80, 80, 80), 2))
    center = size // 2
    line_margin = 4
    painter.drawLine(line_margin, center, size - line_margin, center)  # Horizontaal

    painter.end()
    return pixmap


def save_tree_icons():
    """Sla tree expand/collapse iconen op naar assets folder"""
    import os
    from pathlib import Path

    assets_dir = Path(__file__).parent.parent.parent / "assets"
    assets_dir.mkdir(exist_ok=True)

    expand_icon = create_tree_expand_icon(12)
    expand_icon.save(str(assets_dir / "tree_expand.png"))

    collapse_icon = create_tree_collapse_icon(12)
    collapse_icon.save(str(assets_dir / "tree_collapse.png"))


class IconProvider:
    """Provider voor alle applicatie iconen"""

    _icons = {}
    _tree_icons_saved = False

    @classmethod
    def get_icon(cls, name: str, size: int = 32) -> QIcon:
        """Haal een icoon op bij naam"""
        key = f"{name}_{size}"

        if key not in cls._icons:
            icon_creators = {
                "new": create_3d_document_icon,
                "open": create_3d_folder_icon,
                "save": create_3d_save_icon,
                "print": create_3d_print_icon,
                "cut": create_3d_cut_icon,
                "copy": create_3d_copy_icon,
                "paste": create_3d_paste_icon,
                "chapter": create_3d_chapter_icon,
                "cost_item": create_3d_cost_item_icon,
                "text_row": create_3d_text_row_icon,
                "delete": create_3d_delete_icon,
                "pdf": create_3d_pdf_icon,
                "ifc": create_3d_ifc_icon,
                "dxf": create_3d_dxf_icon,
                "measure": create_3d_measure_icon,
                "zoom_in": create_3d_zoom_in_icon,
                "zoom_out": create_3d_zoom_out_icon,
                "fit": create_3d_fit_icon,
                "excel": create_3d_excel_icon,
                "ods": create_3d_ods_icon,
                "csv": create_3d_csv_icon,
                "up": create_3d_up_icon,
                "down": create_3d_down_icon,
                "indent_in": create_3d_indent_in_icon,
                "indent_out": create_3d_indent_out_icon,
                "calculator": create_3d_calculator_icon,
                "expand": create_3d_expand_icon,
                "collapse": create_3d_collapse_icon,
                "undo": create_3d_undo_icon,
                "redo": create_3d_redo_icon,
                "bold": create_3d_bold_icon,
                "italic": create_3d_italic_icon,
                "underline": create_3d_underline_icon,
                "color": create_3d_color_icon,
                "odt": create_3d_odt_icon,
            }

            if name in icon_creators:
                cls._icons[key] = icon_creators[name](size)
            else:
                # Fallback: leeg icoon
                cls._icons[key] = QIcon()

        return cls._icons[key]
