"""
ProjectPanel - Paneel voor projectgegevens met ERPNext integratie
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLineEdit, QTextEdit, QDateEdit, QLabel, QScrollArea,
    QPushButton, QComboBox, QMessageBox, QDialog, QDialogButtonBox,
    QFrame
)
from PySide6.QtCore import Qt, QDate, Signal
import json
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

# Config bestand pad
CONFIG_DIR = Path.home() / ".opencalc"
ERPNEXT_CONFIG_FILE = CONFIG_DIR / "erpnext_settings.json"


class ERPNextSettingsDialog(QDialog):
    """Dialog voor ERPNext instellingen"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ERPNext Instellingen")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Server instellingen
        server_group = QGroupBox("Server Configuratie")
        server_form = QFormLayout(server_group)

        self._url = QLineEdit()
        self._url.setPlaceholderText("https://uw-erpnext-server.com")
        server_form.addRow("Server URL:", self._url)

        self._api_key = QLineEdit()
        self._api_key.setPlaceholderText("API Key")
        server_form.addRow("API Key:", self._api_key)

        self._api_secret = QLineEdit()
        self._api_secret.setPlaceholderText("API Secret")
        self._api_secret.setEchoMode(QLineEdit.Password)
        server_form.addRow("API Secret:", self._api_secret)

        layout.addWidget(server_group)

        # Test verbinding knop
        test_btn = QPushButton("Test Verbinding")
        test_btn.clicked.connect(self._test_connection)
        layout.addWidget(test_btn)

        # Status label
        self._status_label = QLabel("")
        self._status_label.setStyleSheet("color: #64748b;")
        layout.addWidget(self._status_label)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _test_connection(self):
        """Test de verbinding met ERPNext"""
        url = self._url.text().strip()
        if not url:
            self._status_label.setText("Voer een server URL in")
            self._status_label.setStyleSheet("color: #ef4444;")
            return

        try:
            # Probeer verbinding te maken
            test_url = f"{url}/api/method/frappe.ping"
            req = urllib.request.Request(test_url)
            req.add_header("Authorization", f"token {self._api_key.text()}:{self._api_secret.text()}")
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    self._status_label.setText("Verbinding succesvol!")
                    self._status_label.setStyleSheet("color: #22c55e;")
                else:
                    self._status_label.setText(f"Fout: Status {response.status}")
                    self._status_label.setStyleSheet("color: #ef4444;")
        except urllib.error.URLError as e:
            self._status_label.setText(f"Verbindingsfout: {str(e.reason)}")
            self._status_label.setStyleSheet("color: #ef4444;")
        except Exception as e:
            self._status_label.setText(f"Fout: {str(e)}")
            self._status_label.setStyleSheet("color: #ef4444;")

    def get_settings(self) -> dict:
        """Haal de instellingen op"""
        return {
            "url": self._url.text().strip(),
            "api_key": self._api_key.text().strip(),
            "api_secret": self._api_secret.text().strip()
        }

    def set_settings(self, settings: dict):
        """Stel de instellingen in"""
        self._url.setText(settings.get("url", ""))
        self._api_key.setText(settings.get("api_key", ""))
        self._api_secret.setText(settings.get("api_secret", ""))


class ProjectPanel(QWidget):
    """Paneel voor invoer en weergave van projectgegevens"""

    dataChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._erpnext_settings = {}
        self._load_erpnext_settings()  # Laad opgeslagen instellingen
        self._setup_ui()

    def _setup_ui(self):
        """Stel de UI in"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # ERPNext toolbar bovenaan
        erpnext_toolbar = QFrame()
        erpnext_toolbar.setStyleSheet("""
            QFrame {
                background-color: #f1f5f9;
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        erpnext_layout = QHBoxLayout(erpnext_toolbar)
        erpnext_layout.setContentsMargins(10, 5, 10, 5)

        erpnext_label = QLabel("ERPNext Integratie:")
        erpnext_label.setStyleSheet("font-weight: bold; color: #475569;")
        erpnext_layout.addWidget(erpnext_label)

        self._project_combo = QComboBox()
        self._project_combo.setMinimumWidth(250)
        self._project_combo.setPlaceholderText("Selecteer een project...")
        self._project_combo.currentIndexChanged.connect(self._on_project_selected)
        erpnext_layout.addWidget(self._project_combo)

        refresh_btn = QPushButton("Ophalen")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #0ea5e9;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
            }
            QPushButton:hover {
                background-color: #0284c7;
            }
        """)
        refresh_btn.clicked.connect(self._fetch_projects)
        erpnext_layout.addWidget(refresh_btn)

        settings_btn = QPushButton("Instellingen")
        settings_btn.clicked.connect(self._show_erpnext_settings)
        erpnext_layout.addWidget(settings_btn)

        erpnext_layout.addStretch()

        layout.addWidget(erpnext_toolbar)

        # Scroll area voor formulieren
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(15)

        # Bovenste rij: Projectinformatie en Opdrachtgever naast elkaar
        top_row = QHBoxLayout()
        top_row.setSpacing(15)

        # Projectinformatie groep (links)
        project_group = QGroupBox("Projectinformatie")
        project_form = QFormLayout(project_group)

        self._project_name = QLineEdit()
        self._project_name.setPlaceholderText("Naam van het project")
        project_form.addRow("Projectnaam:", self._project_name)

        self._project_number = QLineEdit()
        self._project_number.setPlaceholderText("Projectnummer of referentie")
        project_form.addRow("Projectnummer:", self._project_number)

        self._project_location = QLineEdit()
        self._project_location.setPlaceholderText("Adres of locatie")
        project_form.addRow("Locatie:", self._project_location)

        self._project_date = QDateEdit()
        self._project_date.setDate(QDate.currentDate())
        self._project_date.setCalendarPopup(True)
        project_form.addRow("Datum:", self._project_date)

        self._project_description = QTextEdit()
        self._project_description.setPlaceholderText("Omschrijving van het project...")
        self._project_description.setMaximumHeight(80)
        project_form.addRow("Omschrijving:", self._project_description)

        top_row.addWidget(project_group)

        # Opdrachtgever groep (rechts)
        client_group = QGroupBox("Opdrachtgever")
        client_form = QFormLayout(client_group)

        self._client_name = QLineEdit()
        self._client_name.setPlaceholderText("Naam opdrachtgever")
        client_form.addRow("Naam:", self._client_name)

        self._client_address = QLineEdit()
        self._client_address.setPlaceholderText("Adres")
        client_form.addRow("Adres:", self._client_address)

        self._client_postal = QLineEdit()
        self._client_postal.setPlaceholderText("Postcode en plaats")
        client_form.addRow("Postcode/Plaats:", self._client_postal)

        self._client_contact = QLineEdit()
        self._client_contact.setPlaceholderText("Contactpersoon")
        client_form.addRow("Contactpersoon:", self._client_contact)

        self._client_phone = QLineEdit()
        self._client_phone.setPlaceholderText("Telefoonnummer")
        client_form.addRow("Telefoon:", self._client_phone)

        self._client_email = QLineEdit()
        self._client_email.setPlaceholderText("E-mailadres")
        client_form.addRow("E-mail:", self._client_email)

        top_row.addWidget(client_group)

        content_layout.addLayout(top_row)

        # Aannemer groep (volle breedte)
        contractor_group = QGroupBox("Aannemer")
        contractor_layout = QHBoxLayout(contractor_group)

        # Linker kolom
        left_form = QFormLayout()
        self._contractor_name = QLineEdit()
        self._contractor_name.setPlaceholderText("Bedrijfsnaam")
        left_form.addRow("Naam:", self._contractor_name)

        self._contractor_address = QLineEdit()
        self._contractor_address.setPlaceholderText("Adres")
        left_form.addRow("Adres:", self._contractor_address)

        self._contractor_postal = QLineEdit()
        self._contractor_postal.setPlaceholderText("Postcode en plaats")
        left_form.addRow("Postcode/Plaats:", self._contractor_postal)

        contractor_layout.addLayout(left_form)

        # Rechter kolom
        right_form = QFormLayout()
        self._contractor_phone = QLineEdit()
        self._contractor_phone.setPlaceholderText("Telefoonnummer")
        right_form.addRow("Telefoon:", self._contractor_phone)

        self._contractor_email = QLineEdit()
        self._contractor_email.setPlaceholderText("E-mailadres")
        right_form.addRow("E-mail:", self._contractor_email)

        self._contractor_kvk = QLineEdit()
        self._contractor_kvk.setPlaceholderText("KvK-nummer")
        right_form.addRow("KvK:", self._contractor_kvk)

        contractor_layout.addLayout(right_form)

        content_layout.addWidget(contractor_group)

        content_layout.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll)

    def _load_erpnext_settings(self):
        """Laad ERPNext instellingen uit JSON bestand"""
        try:
            if ERPNEXT_CONFIG_FILE.exists():
                with open(ERPNEXT_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    self._erpnext_settings = json.load(f)
        except Exception:
            self._erpnext_settings = {}

    def _save_erpnext_settings(self):
        """Sla ERPNext instellingen op naar JSON bestand"""
        try:
            # Maak config directory aan als die niet bestaat
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)

            with open(ERPNEXT_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self._erpnext_settings, f, indent=2)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Opslaan Fout",
                f"Kon instellingen niet opslaan:\n{str(e)}"
            )

    def _show_erpnext_settings(self):
        """Toon ERPNext instellingen dialog"""
        dialog = ERPNextSettingsDialog(self)
        dialog.set_settings(self._erpnext_settings)

        if dialog.exec() == QDialog.Accepted:
            self._erpnext_settings = dialog.get_settings()
            self._save_erpnext_settings()  # Sla op naar JSON
            self._fetch_projects()

    def _fetch_projects(self):
        """Haal projecten op uit ERPNext"""
        if not self._erpnext_settings.get("url"):
            QMessageBox.information(
                self,
                "ERPNext",
                "Configureer eerst de ERPNext instellingen."
            )
            return

        try:
            url = self._erpnext_settings["url"]
            api_key = self._erpnext_settings["api_key"]
            api_secret = self._erpnext_settings["api_secret"]

            # Haal projecten op
            projects_url = f"{url}/api/resource/Project?fields=[\"name\",\"project_name\",\"customer\"]&limit_page_length=100"
            req = urllib.request.Request(projects_url)
            req.add_header("Authorization", f"token {api_key}:{api_secret}")

            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                projects = data.get("data", [])

                self._project_combo.clear()
                self._project_combo.addItem("-- Selecteer een project --", None)

                for project in projects:
                    display_name = project.get("project_name") or project.get("name")
                    self._project_combo.addItem(display_name, project)

                if len(projects) > 0:
                    QMessageBox.information(
                        self,
                        "ERPNext",
                        f"{len(projects)} projecten opgehaald."
                    )
                else:
                    QMessageBox.information(
                        self,
                        "ERPNext",
                        "Geen projecten gevonden."
                    )

        except urllib.error.URLError as e:
            QMessageBox.warning(
                self,
                "ERPNext Fout",
                f"Kan geen verbinding maken met ERPNext:\n{str(e.reason)}"
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                "ERPNext Fout",
                f"Fout bij ophalen projecten:\n{str(e)}"
            )

    def _on_project_selected(self, index: int):
        """Afhandeling van project selectie"""
        project_data = self._project_combo.currentData()
        if not project_data:
            return

        # Vul projectgegevens in
        self._project_name.setText(project_data.get("project_name", ""))
        self._project_number.setText(project_data.get("name", ""))

        # Haal klantgegevens op als customer beschikbaar is
        customer_name = project_data.get("customer")
        if customer_name and self._erpnext_settings.get("url"):
            self._fetch_customer_details(customer_name)

    def _fetch_customer_details(self, customer_name: str):
        """Haal klantgegevens op uit ERPNext"""
        try:
            url = self._erpnext_settings["url"]
            api_key = self._erpnext_settings["api_key"]
            api_secret = self._erpnext_settings["api_secret"]

            customer_url = f"{url}/api/resource/Customer/{urllib.parse.quote(customer_name)}"
            req = urllib.request.Request(customer_url)
            req.add_header("Authorization", f"token {api_key}:{api_secret}")

            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                customer = data.get("data", {})

                self._client_name.setText(customer.get("customer_name", ""))
                # Adres moet apart opgehaald worden via Address doctype
                self._client_email.setText(customer.get("email_id", ""))
                self._client_phone.setText(customer.get("mobile_no", ""))

        except Exception:
            pass  # Negeer fouten bij ophalen klantgegevens

    def get_project_data(self) -> dict:
        """Haal alle projectgegevens op"""
        return {
            "project_name": self._project_name.text(),
            "project_number": self._project_number.text(),
            "project_location": self._project_location.text(),
            "project_date": self._project_date.date().toString("yyyy-MM-dd"),
            "project_description": self._project_description.toPlainText(),
            "client_name": self._client_name.text(),
            "client_address": self._client_address.text(),
            "client_postal": self._client_postal.text(),
            "client_contact": self._client_contact.text(),
            "client_phone": self._client_phone.text(),
            "client_email": self._client_email.text(),
            "contractor_name": self._contractor_name.text(),
            "contractor_address": self._contractor_address.text(),
            "contractor_postal": self._contractor_postal.text(),
            "contractor_phone": self._contractor_phone.text(),
            "contractor_email": self._contractor_email.text(),
            "contractor_kvk": self._contractor_kvk.text(),
        }

    def set_project_data(self, data: dict):
        """Stel projectgegevens in"""
        self._project_name.setText(data.get("project_name", ""))
        self._project_number.setText(data.get("project_number", ""))
        self._project_location.setText(data.get("project_location", ""))
        if data.get("project_date"):
            self._project_date.setDate(QDate.fromString(data["project_date"], "yyyy-MM-dd"))
        self._project_description.setPlainText(data.get("project_description", ""))
        self._client_name.setText(data.get("client_name", ""))
        self._client_address.setText(data.get("client_address", ""))
        self._client_postal.setText(data.get("client_postal", ""))
        self._client_contact.setText(data.get("client_contact", ""))
        self._client_phone.setText(data.get("client_phone", ""))
        self._client_email.setText(data.get("client_email", ""))
        self._contractor_name.setText(data.get("contractor_name", ""))
        self._contractor_address.setText(data.get("contractor_address", ""))
        self._contractor_postal.setText(data.get("contractor_postal", ""))
        self._contractor_phone.setText(data.get("contractor_phone", ""))
        self._contractor_email.setText(data.get("contractor_email", ""))
        self._contractor_kvk.setText(data.get("contractor_kvk", ""))

    def set_erpnext_settings(self, settings: dict):
        """Stel ERPNext instellingen in"""
        self._erpnext_settings = settings

    def get_erpnext_settings(self) -> dict:
        """Haal ERPNext instellingen op"""
        return self._erpnext_settings
