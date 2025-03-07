from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QTableWidget, QTableWidgetItem, QFormLayout,
                              QLineEdit, QComboBox, QTextEdit, QLabel,
                              QMessageBox, QHeaderView)
from PySide6.QtCore import Qt, Slot

class ClientEditor(QWidget):
    """Widget for managing client information"""

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setup_ui()
        self.load_state_codes()
        self.load_clients()

    def setup_ui(self):
        """Initialize the user interface"""
        layout = QHBoxLayout(self)

        # Left side - Client list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Search box
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search clients...")
        self.search_input.textChanged.connect(self.load_clients)
        search_layout.addWidget(self.search_input)
        left_layout.addLayout(search_layout)

        # Client table
        self.client_table = QTableWidget()
        self.client_table.setColumnCount(5)
        self.client_table.setHorizontalHeaderLabels([
            "Name", "Type", "Email", "Phone", "State"
        ])
        self.client_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.client_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.client_table.setSelectionMode(QTableWidget.SingleSelection)
        self.client_table.itemSelectionChanged.connect(self.load_selected_client)
        left_layout.addWidget(self.client_table)

        # Add client button
        self.add_button = QPushButton("Add New Client")
        self.add_button.clicked.connect(self.clear_form)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
        """)
        left_layout.addWidget(self.add_button)

        layout.addWidget(left_widget)

        # Right side - Client details form
        right_widget = QWidget()
        self.form_layout = QFormLayout(right_widget)

        # Client type
        self.client_type_combo = QComboBox()
        self.client_type_combo.addItems(["client", "potential"])
        self.form_layout.addRow("Client Type:", self.client_type_combo)

        # Name
        self.name_edit = QLineEdit()
        self.form_layout.addRow("Name:", self.name_edit)

        # Email
        self.email_edit = QLineEdit()
        self.form_layout.addRow("Email:", self.email_edit)

        # Phone
        self.phone_edit = QLineEdit()
        self.form_layout.addRow("Phone:", self.phone_edit)

        # State
        self.state_combo = QComboBox()
        self.form_layout.addRow("State:", self.state_combo)

        # Address
        self.address_edit = QTextEdit()
        self.address_edit.setMaximumHeight(100)
        self.form_layout.addRow("Address:", self.address_edit)

        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_client)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #198754;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #157347;
            }
        """)
        button_layout.addWidget(self.save_button)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_client)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #bb2d3b;
            }
        """)
        button_layout.addWidget(self.delete_button)

        self.form_layout.addRow("", button_layout)

        layout.addWidget(right_widget)

        # Set stretch factors
        layout.setStretch(0, 3)  # List takes 3 parts
        layout.setStretch(1, 2)  # Form takes 2 parts

        # Style the widget
        self.setStyleSheet("""
            QWidget {
                background-color: white;
            }
            QLineEdit, QTextEdit, QComboBox {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 1px solid #86b7fe;
                outline: none;
            }
            QTableWidget {
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #dee2e6;
            }
        """)

        # Initialize current client id
        self.current_client_id = None

    def load_state_codes(self):
        """Load state codes into combo box"""
        states = self.db_manager.get_state_codes()
        self.state_combo.clear()
        self.state_combo.addItem("", "")  # Empty option
        for state in states:
            self.state_combo.addItem(
                f"{state['code']} - {state['description']}", 
                state['code']
            )

    def load_clients(self):
        """Load clients into table"""
        search_term = self.search_input.text()
        clients = self.db_manager.get_clients(search_term)
        
        self.client_table.setRowCount(len(clients))
        
        for row, client in enumerate(clients):
            self.client_table.setItem(
                row, 0, QTableWidgetItem(client['name'])
            )
            self.client_table.setItem(
                row, 1, QTableWidgetItem(client['client_type'])
            )
            self.client_table.setItem(
                row, 2, QTableWidgetItem(client['email'] or "")
            )
            self.client_table.setItem(
                row, 3, QTableWidgetItem(client['phone'] or "")
            )
            self.client_table.setItem(
                row, 4, QTableWidgetItem(client['state_name'] or "")
            )
            
            # Store client ID in the first cell
            self.client_table.item(row, 0).setData(Qt.UserRole, client['id'])

    @Slot()
    def load_selected_client(self):
        """Load selected client data into form"""
        selected_items = self.client_table.selectedItems()
        if not selected_items:
            return

        # Get client ID from the first cell of selected row
        self.current_client_id = self.client_table.item(
            selected_items[0].row(), 0
        ).data(Qt.UserRole)

        # Get client data
        clients = self.db_manager.get_clients()
        client = next(
            (c for c in clients if c['id'] == self.current_client_id), 
            None
        )
        
        if client:
            # Update form fields
            self.client_type_combo.setCurrentText(client['client_type'])
            self.name_edit.setText(client['name'])
            self.email_edit.setText(client['email'] or "")
            self.phone_edit.setText(client['phone'] or "")
            self.address_edit.setText(client['address'] or "")
            
            # Find and set the correct state in combo box
            state_index = self.state_combo.findData(client['state_code'])
            self.state_combo.setCurrentIndex(state_index)

    @Slot()
    def clear_form(self):
        """Clear the form for new client entry"""
        self.current_client_id = None
        self.client_type_combo.setCurrentIndex(0)
        self.name_edit.clear()
        self.email_edit.clear()
        self.phone_edit.clear()
        self.address_edit.clear()
        self.state_combo.setCurrentIndex(0)
        self.client_table.clearSelection()

    @Slot()
    def save_client(self):
        """Save current client data"""
        # Validate required fields
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Client name is required."
            )
            self.name_edit.setFocus()
            return

        # Prepare client data
        client_data = {
            'name': name,
            'client_type': self.client_type_combo.currentText(),
            'email': self.email_edit.text().strip() or None,
            'phone': self.phone_edit.text().strip() or None,
            'address': self.address_edit.toPlainText().strip() or None,
            'state_code': self.state_combo.currentData() or None
        }

        if self.current_client_id is None:
            # Create new client
            client_id = self.db_manager.create_client(client_data)
            if client_id:
                QMessageBox.information(
                    self,
                    "Success",
                    "Client created successfully."
                )
        else:
            # Update existing client
            client_data['id'] = self.current_client_id
            if self.db_manager.update_client(client_data):
                QMessageBox.information(
                    self,
                    "Success",
                    "Client updated successfully."
                )

        # Refresh client list
        self.load_clients()
        self.clear_form()

    @Slot()
    def delete_client(self):
        """Delete current client"""
        if self.current_client_id is None:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this client?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.db_manager.delete_client(self.current_client_id):
                QMessageBox.information(
                    self,
                    "Success",
                    "Client deleted successfully."
                )
                self.load_clients()
                self.clear_form()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to delete client."
                )
