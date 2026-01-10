"""
Script om het OpenCalc logo te genereren - Premium Design
"""

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import (
    QPixmap, QPainter, QColor, QLinearGradient, QRadialGradient,
    QPen, QBrush, QFont, QPainterPath
)
from PySide6.QtCore import Qt, QRectF, QPointF
import sys
import math


def create_logo(size: int = 512) -> QPixmap:
    """Maak het OpenCalc logo - Premium Modern Design"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.TextAntialiasing)
    painter.setRenderHint(QPainter.SmoothPixmapTransform)

    center = size / 2
    radius = size * 0.45

    # ===== ACHTERGROND MET GRADIENT =====
    # Donkere moderne achtergrond
    bg_gradient = QRadialGradient(center, center, radius * 1.1)
    bg_gradient.setColorAt(0, QColor(30, 58, 95))      # Donker blauw centrum
    bg_gradient.setColorAt(0.7, QColor(15, 23, 42))    # Nog donkerder
    bg_gradient.setColorAt(1, QColor(10, 15, 30))      # Bijna zwart rand

    painter.setBrush(QBrush(bg_gradient))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(QRectF(center - radius, center - radius, radius * 2, radius * 2))

    # Subtiele glow ring
    glow_gradient = QRadialGradient(center, center, radius)
    glow_gradient.setColorAt(0.85, QColor(14, 165, 233, 0))
    glow_gradient.setColorAt(0.95, QColor(14, 165, 233, 80))
    glow_gradient.setColorAt(1.0, QColor(14, 165, 233, 0))

    painter.setBrush(QBrush(glow_gradient))
    painter.drawEllipse(QRectF(center - radius, center - radius, radius * 2, radius * 2))

    # ===== MODERN GEBOUW ICOON =====
    building_gradient = QLinearGradient(0, center - radius * 0.5, 0, center + radius * 0.4)
    building_gradient.setColorAt(0, QColor(255, 255, 255))
    building_gradient.setColorAt(1, QColor(200, 220, 240))

    painter.setBrush(QBrush(building_gradient))
    painter.setPen(Qt.NoPen)

    # Hoofd toren (midden, hoog)
    tower_w = size * 0.14
    tower_h = size * 0.42
    tower_x = center - tower_w / 2 - size * 0.08
    tower_y = center - tower_h * 0.55

    # Tower met afgeronde top
    tower_path = QPainterPath()
    tower_path.moveTo(tower_x, tower_y + tower_h)
    tower_path.lineTo(tower_x, tower_y + size * 0.03)
    tower_path.quadTo(tower_x, tower_y, tower_x + tower_w * 0.2, tower_y)
    tower_path.lineTo(tower_x + tower_w * 0.8, tower_y)
    tower_path.quadTo(tower_x + tower_w, tower_y, tower_x + tower_w, tower_y + size * 0.03)
    tower_path.lineTo(tower_x + tower_w, tower_y + tower_h)
    tower_path.closeSubpath()
    painter.drawPath(tower_path)

    # Tweede gebouw (rechts, lager)
    bld2_w = size * 0.12
    bld2_h = size * 0.32
    bld2_x = tower_x + tower_w + size * 0.02
    bld2_y = center - bld2_h * 0.35

    bld2_path = QPainterPath()
    bld2_path.addRoundedRect(QRectF(bld2_x, bld2_y, bld2_w, bld2_h), size * 0.01, size * 0.01)
    painter.drawPath(bld2_path)

    # Derde gebouw (links, middel)
    bld3_w = size * 0.10
    bld3_h = size * 0.28
    bld3_x = tower_x - bld3_w - size * 0.02
    bld3_y = center - bld3_h * 0.25

    bld3_path = QPainterPath()
    bld3_path.addRoundedRect(QRectF(bld3_x, bld3_y, bld3_w, bld3_h), size * 0.01, size * 0.01)
    painter.drawPath(bld3_path)

    # Ramen in gebouwen (glow effect)
    window_color = QColor(14, 165, 233, 200)
    painter.setBrush(QBrush(window_color))

    win_size = size * 0.025

    # Ramen in hoofdtoren
    for row in range(5):
        for col in range(2):
            wx = tower_x + size * 0.025 + col * (win_size + size * 0.025)
            wy = tower_y + size * 0.05 + row * (win_size + size * 0.025)
            painter.drawRoundedRect(QRectF(wx, wy, win_size, win_size), 2, 2)

    # Ramen in gebouw 2
    for row in range(3):
        wx = bld2_x + (bld2_w - win_size) / 2
        wy = bld2_y + size * 0.03 + row * (win_size + size * 0.025)
        painter.drawRoundedRect(QRectF(wx, wy, win_size, win_size), 2, 2)

    # Ramen in gebouw 3
    for row in range(2):
        wx = bld3_x + (bld3_w - win_size) / 2
        wy = bld3_y + size * 0.03 + row * (win_size + size * 0.025)
        painter.drawRoundedRect(QRectF(wx, wy, win_size, win_size), 2, 2)

    # ===== EURO SYMBOOL MET GLOW =====
    euro_size = size * 0.24
    euro_x = center + size * 0.12
    euro_y = center - size * 0.02

    # Glow achter euro
    euro_glow = QRadialGradient(euro_x + euro_size/2, euro_y + euro_size/2, euro_size * 0.7)
    euro_glow.setColorAt(0, QColor(34, 197, 94, 150))
    euro_glow.setColorAt(0.5, QColor(34, 197, 94, 50))
    euro_glow.setColorAt(1, QColor(34, 197, 94, 0))

    painter.setBrush(QBrush(euro_glow))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(QRectF(euro_x - euro_size*0.2, euro_y - euro_size*0.2,
                               euro_size * 1.4, euro_size * 1.4))

    # Euro cirkel
    euro_gradient = QLinearGradient(euro_x, euro_y, euro_x + euro_size, euro_y + euro_size)
    euro_gradient.setColorAt(0, QColor(34, 197, 94))
    euro_gradient.setColorAt(1, QColor(22, 163, 74))

    painter.setBrush(QBrush(euro_gradient))
    painter.setPen(QPen(QColor(255, 255, 255, 100), size * 0.005))
    painter.drawEllipse(QRectF(euro_x, euro_y, euro_size, euro_size))

    # Euro teken
    painter.setPen(QPen(QColor(255, 255, 255), size * 0.018))
    euro_font = QFont("Arial Black", int(euro_size * 0.45), QFont.Bold)
    painter.setFont(euro_font)
    painter.drawText(QRectF(euro_x, euro_y - size*0.01, euro_size, euro_size), Qt.AlignCenter, "€")

    # ===== GRAFIEK/CHART ELEMENT =====
    chart_y = center + size * 0.22
    chart_x = center - size * 0.22
    bar_width = size * 0.04
    bar_spacing = size * 0.02

    # Oplopende bars (grafiek)
    bar_heights = [size * 0.08, size * 0.12, size * 0.10, size * 0.16, size * 0.14]

    for i, h in enumerate(bar_heights):
        bar_gradient = QLinearGradient(0, chart_y, 0, chart_y - h)
        if i % 2 == 0:
            bar_gradient.setColorAt(0, QColor(14, 165, 233))
            bar_gradient.setColorAt(1, QColor(56, 189, 248))
        else:
            bar_gradient.setColorAt(0, QColor(6, 182, 212))
            bar_gradient.setColorAt(1, QColor(34, 211, 238))

        painter.setBrush(QBrush(bar_gradient))
        painter.setPen(Qt.NoPen)
        bx = chart_x + i * (bar_width + bar_spacing)
        painter.drawRoundedRect(QRectF(bx, chart_y - h, bar_width, h), 3, 3)

    # Trendlijn
    painter.setPen(QPen(QColor(34, 197, 94), size * 0.012, Qt.SolidLine, Qt.RoundCap))
    line_path = QPainterPath()
    points = [
        (chart_x + bar_width/2, chart_y - bar_heights[0] * 0.8),
        (chart_x + (bar_width + bar_spacing) + bar_width/2, chart_y - bar_heights[1] * 0.8),
        (chart_x + 2*(bar_width + bar_spacing) + bar_width/2, chart_y - bar_heights[2] * 0.9),
        (chart_x + 3*(bar_width + bar_spacing) + bar_width/2, chart_y - bar_heights[3] * 0.85),
        (chart_x + 4*(bar_width + bar_spacing) + bar_width/2, chart_y - bar_heights[4] * 0.9),
    ]
    line_path.moveTo(points[0][0], points[0][1])
    for p in points[1:]:
        line_path.lineTo(p[0], p[1])
    painter.drawPath(line_path)

    # ===== SUBTIELE RAND =====
    painter.setBrush(Qt.NoBrush)
    painter.setPen(QPen(QColor(14, 165, 233, 100), size * 0.008))
    painter.drawEllipse(QRectF(center - radius + size*0.01, center - radius + size*0.01,
                               radius * 2 - size*0.02, radius * 2 - size*0.02))

    painter.end()
    return pixmap


def create_simple_logo(size: int = 32) -> QPixmap:
    """Maak een vereenvoudigd logo voor kleine formaten"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    center = size / 2
    radius = size * 0.45

    # Achtergrond
    bg_gradient = QLinearGradient(0, 0, size, size)
    bg_gradient.setColorAt(0, QColor(14, 165, 233))
    bg_gradient.setColorAt(1, QColor(2, 132, 199))

    painter.setBrush(QBrush(bg_gradient))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(QRectF(center - radius, center - radius, radius * 2, radius * 2))

    # Simpel gebouw
    painter.setBrush(QColor(255, 255, 255))
    bw = size * 0.25
    bh = size * 0.4
    bx = center - bw - size * 0.05
    by = center - bh * 0.4
    painter.drawRect(QRectF(bx, by, bw, bh))

    # Euro
    euro_gradient = QLinearGradient(0, 0, size, size)
    euro_gradient.setColorAt(0, QColor(34, 197, 94))
    euro_gradient.setColorAt(1, QColor(22, 163, 74))

    euro_size = size * 0.3
    painter.setBrush(QBrush(euro_gradient))
    painter.drawEllipse(QRectF(center, center - size * 0.1, euro_size, euro_size))

    # Euro teken
    if size >= 24:
        painter.setPen(QPen(QColor(255, 255, 255), max(1, size * 0.06)))
        font = QFont("Arial", max(6, int(euro_size * 0.5)), QFont.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(center, center - size * 0.12, euro_size, euro_size), Qt.AlignCenter, "€")

    painter.end()
    return pixmap


def create_icon_sizes():
    """Maak logo in verschillende formaten"""
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    import os
    os.makedirs("assets", exist_ok=True)

    # Kleine formaten met simpele versie
    for size in [16, 24, 32]:
        pixmap = create_simple_logo(size)
        pixmap.save(f"assets/logo_{size}.png")
        print(f"Logo {size}x{size} opgeslagen (simpel)")

    # Grotere formaten met volledige versie
    for size in [48, 64, 128, 256, 512]:
        pixmap = create_logo(size)
        pixmap.save(f"assets/logo_{size}.png")
        print(f"Logo {size}x{size} opgeslagen")

    # Hoofdlogo
    main_logo = create_logo(512)
    main_logo.save("assets/logo.png")
    print("Hoofdlogo opgeslagen als assets/logo.png")

    # ICO bestand
    ico_logo = create_logo(256)
    ico_logo.save("assets/opencalc.ico")
    print("ICO bestand opgeslagen")


if __name__ == "__main__":
    create_icon_sizes()
    print("\nAlle logo bestanden zijn aangemaakt!")
