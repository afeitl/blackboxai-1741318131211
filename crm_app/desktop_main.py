import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
import mysql.connector
from database import DatabaseManager
from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from ui.client_editor import ClientEditor
from ui.employee_editor import EmployeeEditor
from ui.schedule_manager import ScheduleManager
from ui.report_viewer import ReportViewer

class CRMApplication:
    """Main CRM desktop application class"""

    def __init__(self):
        # Create the application
        self.app = QApplication(sys.argv)
        self.app.setStyle('Fusion')  # Use Fusion style for modern look

        # Set application-wide stylesheet
        self.app.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #212529;
            }
            QMessageBox QPushButton {
                background-color: #0d6efd;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                min-width: 60px;
            }
            QMessageBox QPushButton:hover {
                background-color: #0b5ed7;
            }
        """)

        # Initialize database connection
        self.db_manager = DatabaseManager(
            host='localhost',
            database='crm_db',
            user='root',
            password=''  # Set your database password here
        )

        # Connect to database
        if not self.db_manager.connect():
            print("Error: Could not connect to database.")
            sys.exit(1)

    def run(self):
        """Run the application"""
        # Create and show login window
        login_window = LoginWindow(self.db_manager)
        login_window.login_successful.connect(self.show_main_window)

        # Center the login window on screen
        screen_geometry = self.app.primaryScreen().geometry()
        x = (screen_geometry.width() - login_window.width()) // 2
        y = (screen_geometry.height() - login_window.height()) // 2
        login_window.move(x, y)

        login_window.show()

        # Start the event loop
        return self.app.exec()

    def show_main_window(self, user_data):
        """Show main window after successful login"""
        # Create main window
        self.main_window = MainWindow(self.db_manager, user_data)

        # Create and add components
        client_editor = ClientEditor(self.db_manager)
        self.main_window.add_widget('clients', client_editor)

        schedule_manager = ScheduleManager(self.db_manager, user_data)
        self.main_window.add_widget('contacts', schedule_manager)

        report_viewer = ReportViewer(self.db_manager, user_data)
        self.main_window.add_widget('reports', report_viewer)

        # Add employee editor only for managers
        if user_data['role'] == 'manager':
            employee_editor = EmployeeEditor(self.db_manager)
            self.main_window.add_widget('employees', employee_editor)

        # Center the main window on screen
        screen_geometry = self.app.primaryScreen().geometry()
        x = (screen_geometry.width() - self.main_window.width()) // 2
        y = (screen_geometry.height() - self.main_window.height()) // 2
        self.main_window.move(x, y)

        self.main_window.show()

def main():
    """Application entry point"""
    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # Create and run application
    crm_app = CRMApplication()
    sys.exit(crm_app.run())

if __name__ == '__main__':
    main()
