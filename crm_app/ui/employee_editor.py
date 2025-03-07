from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QTableWidget, QTableWidgetItem, QFormLayout,
                              QLineEdit, QComboBox, QLabel, QMessageBox,
                              QHeaderView)
from PySide6.QtCore import Qt, Slot
import bcrypt

class EmployeeEditor(QWidget):
    """Widget for managing employee information"""

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setup_ui()
        self.load_employees()

    def setup_ui(self):
        """Initialize the user interface"""
        layout = QHBoxLayout(self)

        # Left side - Employee list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Employee table
        self.employee_table = QTableWidget()
        self.employee_table.setColumnCount(3)
        self.employee_table.setHorizontalHeaderLabels([
            "Name", "Login ID", "Role"
        ])
        self.employee_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.employee_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.employee_table.setSelectionMode(QTableWidget.SingleSelection)
        self.employee_table.itemSelectionChanged.connect(self.load_selected_employee)
        left_layout.addWidget(self.employee_table)

        # Add employee button
        self.add_button = QPushButton("Add New Employee")
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

        # Right side - Employee details form
        right_widget = QWidget()
        self.form_layout = QFormLayout(right_widget)

        # Name
        self.name_edit = QLineEdit()
        self.form_layout.addRow("Name:", self.name_edit)

        # Login ID
        self.login_id_edit = QLineEdit()
        self.form_layout.addRow("Login ID:", self.login_id_edit)

        # Password
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.form_layout.addRow("Password:", self.password_edit)

        # Password confirmation
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        self.form_layout.addRow("Confirm Password:", self.confirm_password_edit)

        # Role
        self.role_combo = QComboBox()
        self.role_combo.addItems(["employee", "manager"])
        self.form_layout.addRow("Role:", self.role_combo)

        # Password note
        password_note = QLabel(
            "Note: Leave password fields empty to keep existing password"
        )
        password_note.setStyleSheet("color: #6c757d; font-size: 12px;")
        self.form_layout.addRow("", password_note)

        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_employee)
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
        self.delete_button.clicked.connect(self.delete_employee)
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
            QLineEdit, QComboBox {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
            }
            QLineEdit:focus, QComboBox:focus {
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

        # Initialize current employee id
        self.current_employee_id = None

    def load_employees(self):
        """Load employees into table"""
        employees = self.db_manager.get_employees()
        
        self.employee_table.setRowCount(len(employees))
        
        for row, employee in enumerate(employees):
            self.employee_table.setItem(
                row, 0, QTableWidgetItem(employee['name'])
            )
            self.employee_table.setItem(
                row, 1, QTableWidgetItem(employee['login_id'])
            )
            self.employee_table.setItem(
                row, 2, QTableWidgetItem(employee['role'])
            )
            
            # Store employee ID in the first cell
            self.employee_table.item(row, 0).setData(Qt.UserRole, employee['id'])

    @Slot()
    def load_selected_employee(self):
        """Load selected employee data into form"""
        selected_items = self.employee_table.selectedItems()
        if not selected_items:
            return

        # Get employee ID from the first cell of selected row
        self.current_employee_id = self.employee_table.item(
            selected_items[0].row(), 0
        ).data(Qt.UserRole)

        # Get employee data
        employees = self.db_manager.get_employees()
        employee = next(
            (e for e in employees if e['id'] == self.current_employee_id), 
            None
        )
        
        if employee:
            # Update form fields
            self.name_edit.setText(employee['name'])
            self.login_id_edit.setText(employee['login_id'])
            self.role_combo.setCurrentText(employee['role'])
            
            # Clear password fields
            self.password_edit.clear()
            self.confirm_password_edit.clear()

    @Slot()
    def clear_form(self):
        """Clear the form for new employee entry"""
        self.current_employee_id = None
        self.name_edit.clear()
        self.login_id_edit.clear()
        self.password_edit.clear()
        self.confirm_password_edit.clear()
        self.role_combo.setCurrentIndex(0)
        self.employee_table.clearSelection()

    @Slot()
    def save_employee(self):
        """Save current employee data"""
        # Validate required fields
        name = self.name_edit.text().strip()
        login_id = self.login_id_edit.text().strip()
        password = self.password_edit.text()
        confirm_password = self.confirm_password_edit.text()
        role = self.role_combo.currentText()

        if not name or not login_id:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Name and Login ID are required."
            )
            return

        # For new employee, password is required
        if self.current_employee_id is None and not password:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Password is required for new employees."
            )
            return

        # Validate password confirmation if password is being changed
        if password:
            if password != confirm_password:
                QMessageBox.warning(
                    self,
                    "Validation Error",
                    "Passwords do not match."
                )
                return

        # Prepare employee data
        employee_data = {
            'name': name,
            'login_id': login_id,
            'role': role
        }

        if password:
            employee_data['password'] = password

        if self.current_employee_id is None:
            # Create new employee
            employee_id = self.db_manager.create_employee(employee_data)
            if employee_id:
                QMessageBox.information(
                    self,
                    "Success",
                    "Employee created successfully."
                )
        else:
            # Update existing employee
            employee_data['id'] = self.current_employee_id
            if self.db_manager.update_employee(employee_data):
                QMessageBox.information(
                    self,
                    "Success",
                    "Employee updated successfully."
                )

        # Refresh employee list
        self.load_employees()
        self.clear_form()

    @Slot()
    def delete_employee(self):
        """Delete current employee"""
        if self.current_employee_id is None:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this employee?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.db_manager.delete_employee(self.current_employee_id):
                QMessageBox.information(
                    self,
                    "Success",
                    "Employee deleted successfully."
                )
                self.load_employees()
                self.clear_form()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to delete employee."
                )
