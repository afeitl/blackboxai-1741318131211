from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QStackedWidget, QMessageBox)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QIcon, QFont

class MainWindow(QMainWindow):
    """Main window of the CRM application"""
    
    def __init__(self, db_manager, user_data, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user_data = user_data  # Contains user id, name, role, etc.
        self.setup_ui()

    def setup_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Business CRM")
        self.setMinimumSize(1024, 768)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Create sidebar for navigation
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)

        # Create stacked widget for main content
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack)

        # Set layout proportions (sidebar:content = 1:4)
        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 4)

        # Style the window
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QPushButton {
                text-align: left;
                padding: 12px;
                border: none;
                border-radius: 4px;
                margin: 2px 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
            QPushButton:checked {
                background-color: #0d6efd;
                color: white;
            }
            QLabel#UserLabel {
                padding: 16px;
                font-size: 14px;
                color: #495057;
            }
        """)

    def _create_sidebar(self):
        """Create the navigation sidebar"""
        sidebar = QWidget()
        sidebar.setMaximumWidth(250)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: white;
                border-right: 1px solid #dee2e6;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Add user info at the top
        user_label = QLabel(f"Welcome, {self.user_data['name']}")
        user_label.setObjectName("UserLabel")
        user_label.setWordWrap(True)
        layout.addWidget(user_label)

        # Add navigation buttons
        self.nav_buttons = {}
        
        # Clients button
        self.nav_buttons['clients'] = self._create_nav_button(
            "Clients", "fas fa-users", "Manage clients and potential clients"
        )
        layout.addWidget(self.nav_buttons['clients'])

        # Contacts button
        self.nav_buttons['contacts'] = self._create_nav_button(
            "Contacts", "fas fa-address-book", "Manage contact schedules"
        )
        layout.addWidget(self.nav_buttons['contacts'])

        # Reports button
        self.nav_buttons['reports'] = self._create_nav_button(
            "Reports", "fas fa-chart-bar", "View contact reports"
        )
        layout.addWidget(self.nav_buttons['reports'])

        # Show employee management only for managers
        if self.user_data['role'] == 'manager':
            self.nav_buttons['employees'] = self._create_nav_button(
                "Employees", "fas fa-user-tie", "Manage employees"
            )
            layout.addWidget(self.nav_buttons['employees'])

        # Add stretch to push logout to bottom
        layout.addStretch()

        # Add logout button at the bottom
        self.logout_button = self._create_nav_button(
            "Logout", "fas fa-sign-out-alt", "Logout from the application"
        )
        self.logout_button.clicked.connect(self.logout)
        layout.addWidget(self.logout_button)

        return sidebar

    def _create_nav_button(self, text, icon_name, tooltip):
        """Create a navigation button with icon and text"""
        button = QPushButton(f" {text}")
        button.setIcon(self._get_icon(icon_name))
        button.setCheckable(True)
        button.setToolTip(tooltip)
        button.setFont(QFont("Arial", 10))
        return button

    def _get_icon(self, name):
        """Create an icon from Font Awesome class name"""
        # This is a placeholder - actual icon implementation will depend on
        # how we include Font Awesome in the application
        return QIcon()

    @Slot()
    def logout(self):
        """Handle logout action"""
        reply = QMessageBox.question(
            self,
            "Confirm Logout",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.close()

    def add_widget(self, name, widget):
        """Add a widget to the content stack"""
        self.content_stack.addWidget(widget)
        if name in self.nav_buttons:
            self.nav_buttons[name].clicked.connect(
                lambda: self.content_stack.setCurrentWidget(widget)
            )

    def closeEvent(self, event):
        """Handle window close event"""
        self.db_manager.close()
        event.accept()
