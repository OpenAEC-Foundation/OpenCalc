# OpenCalc

<p align="center">
  <img src="assets/logo.png" alt="OpenCalc Logo" width="200"/>
</p>

<p align="center">
  <strong>Open-source bouwkostenbegroting software</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installatie">Installatie</a> •
  <a href="#gebruik">Gebruik</a> •
  <a href="#technologie">Technologie</a> •
  <a href="#bijdragen">Bijdragen</a>
</p>

---

## Over OpenCalc

OpenCalc is een moderne, open-source applicatie voor het maken van bouwkostenbegrotingen. De software ondersteunt het IFC (Industry Foundation Classes) formaat en is volledig compatibel met de Nederlandse STABU-systematiek en SFB-codering.

## Features

### Begroting
- **Hiërarchische structuur** - Hoofdstukken en kostenposten met inklapbare weergave
- **STABU-codering** - Volledige ondersteuning voor STABU-codes
- **SFB-codering** - Extra kolom voor SFB-classificatie
- **Automatische berekeningen** - Subtotalen, BTW en eindtotalen
- **Meerdere documenten** - Werk met meerdere begrotingen tegelijk via tabs
- **Tekstregels** - Voeg opmerkingen toe zonder hoeveelheid/kosteninformatie
- **Tekstopmaak** - Vet, cursief, onderstreept en kleur voor tekst
- **Ongedaan maken/Opnieuw** - Volledige undo/redo ondersteuning
- **Zoomen** - Ctrl+Scroll om in/uit te zoomen op de begroting

### Import/Export
- **IFC ondersteuning** - Lees en schrijf IFC-bestanden (Industry Foundation Classes)
- **Excel export** - Exporteer naar .xlsx formaat
- **ODS export** - Exporteer naar OpenDocument Spreadsheet (LibreOffice Calc)
- **ODT export** - Exporteer naar OpenDocument Text (LibreOffice Writer)
- **PDF export** - Genereer professionele PDF-rapporten
- **HTML export** - Exporteer naar HTML formaat
- **CSV import** - Importeer gegevens uit CSV-bestanden

### Documenten
- **PDF viewer** - Bekijk en annoteer PDF-bestanden
- **IFC 3D viewer** - 3D visualisatie van BIM-modellen
- **DXF/DWG ondersteuning** - Bekijk technische tekeningen

### Projectbeheer
- **Projectgegevens** - Beheer project-, opdrachtgever- en aannemergegevens
- **Opslagen** - Configureer algemene kosten, winst en risico
- **Rapporten** - Genereer gedetailleerde rapportages
- **Offertes** - Maak professionele offertes met preview

### Interface
- **Modern ribbon interface** - Office-stijl toolbar voor snelle toegang
- **Dockable panels** - Flexibele indeling van vensters
- **Eigenschappen paneel** - Bekijk en bewerk item eigenschappen
- **Context menu's** - Rechtsklik voor snelle acties

## Installatie

### Vereisten
- Python 3.10 of hoger
- Windows, Linux of macOS

### Stappen

1. **Clone de repository**
   ```bash
   git clone https://github.com/yourusername/OpenCalc.git
   cd OpenCalc
   ```

2. **Maak een virtuele omgeving**
   ```bash
   python -m venv .venv

   # Windows
   .venv\Scripts\activate

   # Linux/macOS
   source .venv/bin/activate
   ```

3. **Installeer dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start de applicatie**
   ```bash
   python main.py
   ```

### Dependencies

| Package | Versie | Beschrijving |
|---------|--------|--------------|
| PySide6 | ≥6.5.0 | Qt6 bindings voor Python |
| PySide6-WebEngine | ≥6.5.0 | Web content rendering |
| ifcopenshell | ≥0.7.0 | IFC bestandsondersteuning |
| openpyxl | ≥3.1.0 | Excel bestandsondersteuning |
| odfpy | ≥1.4.0 | ODS/ODT bestandsondersteuning |
| reportlab | ≥4.0.0 | PDF generatie |

## Gebruik

### Nieuwe begroting maken
1. Klik op **Nieuw** in de ribbon of gebruik `Ctrl+N`
2. Voeg hoofdstukken toe via **Hoofdstuk** knop
3. Voeg kostenposten toe via **Kostenpost** knop
4. Vul STABU-code, omschrijving, hoeveelheid en prijs in

### IFC bestand openen
1. Klik op **Openen** of gebruik `Ctrl+O`
2. Selecteer een `.ifc` bestand
3. De begroting wordt automatisch geladen

### Exporteren
- **PDF**: Start tab → Exporteren → PDF Export
- **Excel**: Start tab → Exporteren → Excel Export
- **ODS**: Start tab → Exporteren → ODS Export

### Sneltoetsen

| Sneltoets | Actie |
|-----------|-------|
| `Ctrl+N` | Nieuwe begroting |
| `Ctrl+O` | Openen |
| `Ctrl+S` | Opslaan |
| `Ctrl+Shift+S` | Opslaan als |
| `Ctrl+P` | Afdrukken |
| `Ctrl+Z` | Ongedaan maken |
| `Ctrl+Y` | Opnieuw |
| `Ctrl+X` | Knippen |
| `Ctrl+C` | Kopiëren |
| `Ctrl+V` | Plakken |
| `Delete` | Verwijderen |
| `Ctrl+Scroll` | In/uitzoomen |

## Technologie

OpenCalc is gebouwd met moderne technologieën:

- **Python 3.10+** - Programmeertaal
- **PySide6 (Qt6)** - GUI framework
- **IfcOpenShell** - IFC parsing en manipulatie
- **OpenPyXL** - Excel ondersteuning
- **ReportLab** - PDF generatie

### Architectuur

```
OpenCalc/
├── main.py                 # Applicatie entry point
├── src/
│   ├── models/            # Data modellen
│   │   ├── cost_item.py   # Kostenpost model
│   │   ├── cost_value.py  # Waarde model
│   │   └── cost_schedule.py # Begroting model
│   ├── ui/                # User interface
│   │   ├── main_window.py # Hoofdvenster
│   │   ├── ribbon.py      # Ribbon toolbar
│   │   ├── cost_table.py  # Kostentabel
│   │   └── ...
│   ├── ifc/               # IFC handling
│   │   ├── ifc_handler.py # IFC bestandsbeheer
│   │   └── cost_api.py    # Cost API
│   └── services/          # Services
│       ├── export_service.py
│       └── print_service.py
├── assets/                # Logo en iconen
├── voorbeelden/           # Voorbeeld bestanden
└── requirements.txt
```

## STABU en SFB

### STABU-systematiek
OpenCalc ondersteunt de STABU-codering voor Nederlandse bouwbestekken:
- **Hoofdstukken** (bijv. 01, 02, 03...)
- **Paragrafen** (bijv. 01.01, 01.02...)
- **Artikelen** (bijv. 01.01.01...)

### SFB-codering
Optionele SFB (Samenwerkingsverband Functionele Bouw) codering:
- Functionele classificatie van bouwelementen
- Internationale standaard voor bouwclassificatie

## Cross-platform

OpenCalc werkt op:
- **Windows** 10/11
- **Linux** (Ubuntu, Fedora, etc.)
- **macOS** (Intel en Apple Silicon)

## Bijdragen

Bijdragen zijn welkom!

### Ontwikkeling

1. Fork de repository
2. Maak een feature branch (`git checkout -b feature/nieuwe-feature`)
3. Commit je wijzigingen (`git commit -m 'Voeg nieuwe feature toe'`)
4. Push naar de branch (`git push origin feature/nieuwe-feature`)
5. Open een Pull Request

## Licentie

Dit project is gelicenseerd onder de MIT License - zie het [LICENSE](LICENSE) bestand voor details.

## Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/OpenCalc/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/OpenCalc/discussions)

---

<p align="center">
  Gemaakt met ❤️ voor de Nederlandse bouwsector
</p>
