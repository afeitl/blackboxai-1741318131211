from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QPushButton, QMessageBox)
from PySide6.QtCore import Qt, Signal

class LoginWindow(QDialog):
    """Login dialog window that appears before accessing the main application"""
    
    # Signal emitted when login is successful
    login_successful = Signal(dict)  # Emits user data dictionary

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setup_ui()

    def setup_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("CRM Login")
        self.setModal(True)
        self.setMinimumWidth(300)

        # Create layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Add title
        title_label = QLabel("Business CRM")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                margin: 20px;
            }
        """)
        layout.addWidget(title_label)

        # Login ID field
        layout.addWidget(QLabel("Login ID:"))
        self.login_id_edit = QLineEdit()
        self.login_id_edit.setPlaceholderText("Enter your login ID")
        layout.addWidget(self.login_id_edit)

        # Password field
        layout.addWidget(QLabel("Password:"))
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Enter your password")
        self.password_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_edit)

        # Login button
        button_layout = QHBoxLayout()
        self.login_button = QPushButton("Login")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
            QPushButton:pressed {
                background-color: #0a58ca;
            }
        """)
        self.login_button.clicked.connect(self.attempt_login)
        button_layout.addStretch()
        button_layout.addWidget(self.login_button)
        layout.addLayout(button_layout)

        # Add some spacing
        layout.addSpacing(20)

        # Set window style
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                font-size: 14px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #86b7fe;
                outline: none;
            }
        """)

        # Set focus on login field
        self.login_id_edit.setFocus()

        # Connect enter key to login
        self.login_id_edit.returnPressed.connect(self.attempt_login)
        self.password_edit.returnPressed.connect(self.attempt_login)

    def attempt_login(self):
        """Verify login credentials and emit signal if successful"""
        login_id = self.login_id_edit.text().strip()
        password = self.password_edit.text()

        if not login_id or not password:
            QMessageBox.warning(
                self,
                "Login Error",
                "Please enter both login ID and password."
            )
            return

        # Attempt to verify credentials
        user_data = self.db_manager.verify_login(login_id, password)
        
        if user_data:
            self.login_successful.emit(user_data)
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Login Failed",
                "Invalid login ID or password. Please try again."
            )
            self.password_edit.clear()
            self.password_edit.setFocus()

    def keyPressEvent(self, event):
        """Override keyPressEvent to prevent closing dialog with Escape key"""
        if event.key() != Qt.Key_Escape:
            super().keyPressEvent(event)
