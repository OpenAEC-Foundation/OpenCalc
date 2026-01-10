#!/usr/bin/env python3
"""
OpenCalc - IFC-gebaseerd kostenbegrotingsprogramma
Open source bouwkostenbegroting met IFC als bestandsformaat
"""

import sys
import argparse
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTimer
from src.ui.main_window import MainWindow


def main():
    # Parse commandline argumenten
    parser = argparse.ArgumentParser(description="OpenCalc - Bouwkostenbegroting")
    parser.add_argument("file", nargs="?", help="IFC bestand om te openen")
    parser.add_argument("--pdf", help="PDF bestand om te openen in viewer")
    parser.add_argument("--ifc3d", help="IFC bestand voor 3D viewer")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    app.setApplicationName("OpenCalc")
    app.setOrganizationName("OpenCalc")
    app.setApplicationVersion("0.2.0")

    # Stel applicatie icoon in
    icon_path = Path(__file__).parent / "resources" / "icons" / "app_icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow(initial_file=args.file)
    window.show()

    # Open PDF of IFC3D bestanden na een korte delay (zodat UI geladen is)
    def open_extra_files():
        if args.pdf:
            window._doc_viewer.show()
            window._ribbon._toggle_docs_btn.setChecked(True)
            window._doc_viewer.open_pdf_file(args.pdf)
            # Pas splitter aan
            sizes = window._main_splitter.sizes()
            total = sum(sizes)
            window._main_splitter.setSizes([int(total * 0.45), 0, int(total * 0.55)])
        if args.ifc3d:
            window._ifc_3d_viewer.show()
            window._ifc_3d_viewer.load_file(args.ifc3d)

    if args.pdf or args.ifc3d:
        QTimer.singleShot(500, open_extra_files)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
