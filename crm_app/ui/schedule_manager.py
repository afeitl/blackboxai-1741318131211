from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QTableWidget, QTableWidgetItem, QFormLayout,
                              QLineEdit, QComboBox, QTextEdit, QLabel,
                              QMessageBox, QHeaderView, QDateTimeEdit)
from PySide6.QtCore import Qt, Slot, QDateTime
from datetime import datetime

class ScheduleManager(QWidget):
    """Widget for managing client contact schedules"""

    def __init__(self, db_manager, user_data, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user_data = user_data  # Contains user id, role, etc.
        self.setup_ui()
        self.load_contacts()

    def setup_ui(self):
        """Initialize the user interface"""
        layout = QHBoxLayout(self)

        # Left side - Contact schedule list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Contact table
        self.contact_table = QTableWidget()
        self.contact_table.setColumnCount(6)
        self.contact_table.setHorizontalHeaderLabels([
            "Client Name", "Date/Time", "Method", "Rating", "Notes", "Status"
        ])
        self.contact_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.contact_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.contact_table.setSelectionMode(QTableWidget.SingleSelection)
        self.contact_table.itemSelectionChanged.connect(self.load_selected_contact)
        left_layout.addWidget(self.contact_table)

        # Add contact button
        self.add_button = QPushButton("Schedule New Contact")
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

        # Right side - Contact details form
        right_widget = QWidget()
        self.form_layout = QFormLayout(right_widget)

        # Client selection
        self.client_combo = QComboBox()
        self.form_layout.addRow("Client:", self.client_combo)

        # Date and time
        self.datetime_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.datetime_edit.setCalendarPopup(True)
        self.form_layout.addRow("Date/Time:", self.datetime_edit)

        # Contact method
        self.method_combo = QComboBox()
        self.method_combo.addItems(["phone", "email", "in-person", "other"])
        self.form_layout.addRow("Contact Method:", self.method_combo)

        # Conversion rating
        self.rating_combo = QComboBox()
        self.rating_combo.addItems([""] + [str(i) for i in range(1, 6)])
        self.form_layout.addRow("Conversion Rating:", self.rating_combo)

        # Notes
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(100)
        self.form_layout.addRow("Notes:", self.notes_edit)

        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Scheduled", "Completed", "Cancelled"])
        self.form_layout.addRow("Status:", self.status_combo)

        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_contact)
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
        self.delete_button.clicked.connect(self.delete_contact)
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
            QLineEdit, QTextEdit, QComboBox, QDateTimeEdit {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateTimeEdit:focus {
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

        # Initialize current contact id and load clients
        self.current_contact_id = None
        self.load_clients()

    def load_clients(self):
        """Load clients into combo box"""
        clients = self.db_manager.get_clients()
        self.client_combo.clear()
        for client in clients:
            self.client_combo.addItem(
                f"{client['name']} ({client['client_type']})",
                client['id']
            )

    def load_contacts(self):
        """Load contacts into table"""
        # Get contacts based on user role
        contacts = self.db_manager.get_employee_contacts(
            self.user_data['id'],
            self.user_data['role'] == 'manager'
        )
        
        self.contact_table.setRowCount(len(contacts))
        
        for row, contact in enumerate(contacts):
            self.contact_table.setItem(
                row, 0, QTableWidgetItem(contact['client_name'])
            )
            # Format datetime
            dt = contact['contact_datetime'].strftime("%Y-%m-%d %H:%M")
            self.contact_table.setItem(row, 1, QTableWidgetItem(dt))
            self.contact_table.setItem(
                row, 2, QTableWidgetItem(contact['contact_method'])
            )
            rating = str(contact['conversion_rating']) if contact['conversion_rating'] else ""
            self.contact_table.setItem(row, 3, QTableWidgetItem(rating))
            self.contact_table.setItem(
                row, 4, QTableWidgetItem(contact['notes'] or "")
            )
            self.contact_table.setItem(
                row, 5, QTableWidgetItem(contact['status'])
            )
            
            # Store contact ID in the first cell
            self.contact_table.item(row, 0).setData(Qt.UserRole, contact['id'])

    @Slot()
    def load_selected_contact(self):
        """Load selected contact data into form"""
        selected_items = self.contact_table.selectedItems()
        if not selected_items:
            return

        # Get contact ID from the first cell of selected row
        self.current_contact_id = self.contact_table.item(
            selected_items[0].row(), 0
        ).data(Qt.UserRole)

        # Get contact data
        contacts = self.db_manager.get_employee_contacts(
            self.user_data['id'],
            self.user_data['role'] == 'manager'
        )
        contact = next(
            (c for c in contacts if c['id'] == self.current_contact_id), 
            None
        )
        
        if contact:
            # Find and set client in combo box
            client_index = self.client_combo.findData(contact['client_id'])
            self.client_combo.setCurrentIndex(client_index)
            
            # Set datetime
            self.datetime_edit.setDateTime(contact['contact_datetime'])
            
            # Set method
            self.method_combo.setCurrentText(contact['contact_method'])
            
            # Set rating
            rating = str(contact['conversion_rating']) if contact['conversion_rating'] else ""
            rating_index = self.rating_combo.findText(rating)
            self.rating_combo.setCurrentIndex(rating_index)
            
            # Set notes
            self.notes_edit.setText(contact['notes'] or "")
            
            # Set status
            self.status_combo.setCurrentText(contact['status'])

    @Slot()
    def clear_form(self):
        """Clear the form for new contact entry"""
        self.current_contact_id = None
        self.client_combo.setCurrentIndex(0)
        self.datetime_edit.setDateTime(QDateTime.currentDateTime())
        self.method_combo.setCurrentIndex(0)
        self.rating_combo.setCurrentIndex(0)
        self.notes_edit.clear()
        self.status_combo.setCurrentIndex(0)
        self.contact_table.clearSelection()

    @Slot()
    def save_contact(self):
        """Save current contact data"""
        # Validate required fields
        if self.client_combo.currentIndex() == -1:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please select a client."
            )
            return

        # Prepare contact data
        contact_data = {
            'client_id': self.client_combo.currentData(),
            'employee_id': self.user_data['id'],
            'contact_datetime': self.datetime_edit.dateTime().toPython(),
            'contact_method': self.method_combo.currentText(),
            'status': self.status_combo.currentText(),
            'notes': self.notes_edit.toPlainText().strip() or None
        }

        # Add rating if selected
        rating_text = self.rating_combo.currentText()
        if rating_text:
            contact_data['conversion_rating'] = int(rating_text)

        if self.current_contact_id is None:
            # Create new contact
            contact_id = self.db_manager.create_contact(contact_data)
            if contact_id:
                QMessageBox.information(
                    self,
                    "Success",
                    "Contact scheduled successfully."
                )
        else:
            # Update existing contact
            contact_data['id'] = self.current_contact_id
            if self.db_manager.update_contact(contact_data):
                QMessageBox.information(
                    self,
                    "Success",
                    "Contact updated successfully."
                )

        # Refresh contact list
        self.load_contacts()
        self.clear_form()

    @Slot()
    def delete_contact(self):
        """Delete current contact"""
        if self.current_contact_id is None:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this contact?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.db_manager.delete_contact(self.current_contact_id):
                QMessageBox.information(
                    self,
                    "Success",
                    "Contact deleted successfully."
                )
                self.load_contacts()
                self.clear_form()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to delete contact."
                )
