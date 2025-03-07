from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QTableWidget, QTableWidgetItem, QLabel,
                              QDateEdit, QComboBox, QHeaderView)
from PySide6.QtCore import Qt, Slot, QDate
from datetime import datetime, timedelta

class ReportViewer(QWidget):
    """Widget for viewing contact reports with role-based filtering"""

    def __init__(self, db_manager, user_data, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user_data = user_data  # Contains user id, role, etc.
        self.setup_ui()
        self.load_reports()

    def setup_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)

        # Filter controls
        filter_layout = QHBoxLayout()

        # Date range
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("From:"))
        self.start_date = QDateEdit(QDate.currentDate().addDays(-30))
        self.start_date.setCalendarPopup(True)
        date_layout.addWidget(self.start_date)
        
        date_layout.addWidget(QLabel("To:"))
        self.end_date = QDateEdit(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        date_layout.addWidget(self.end_date)
        filter_layout.addLayout(date_layout)

        # Quick date filters
        self.period_combo = QComboBox()
        self.period_combo.addItems([
            "Custom Range", "Today", "This Week", "This Month", "Last 30 Days"
        ])
        self.period_combo.currentTextChanged.connect(self.update_date_range)
        filter_layout.addWidget(self.period_combo)

        # Status filter
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All Status", "Scheduled", "Completed", "Cancelled"])
        filter_layout.addWidget(self.status_combo)

        # Employee filter (only for managers)
        if self.user_data['role'] == 'manager':
            self.employee_combo = QComboBox()
            self.employee_combo.addItem("All Employees")
            self.load_employees()
            filter_layout.addWidget(self.employee_combo)

        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_reports)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
        """)
        filter_layout.addWidget(self.refresh_button)

        layout.addLayout(filter_layout)

        # Reports table
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(7)
        self.report_table.setHorizontalHeaderLabels([
            "Date/Time", "Client Name", "Type", "Employee",
            "Method", "Rating", "Status"
        ])
        self.report_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        layout.addWidget(self.report_table)

        # Summary section
        summary_layout = QHBoxLayout()
        
        # Total contacts
        self.total_label = QLabel()
        summary_layout.addWidget(self.total_label)
        
        # Average rating
        self.rating_label = QLabel()
        summary_layout.addWidget(self.rating_label)
        
        # Completion rate
        self.completion_label = QLabel()
        summary_layout.addWidget(self.completion_label)
        
        summary_layout.addStretch()
        layout.addLayout(summary_layout)

        # Style the widget
        self.setStyleSheet("""
            QWidget {
                background-color: white;
            }
            QLabel {
                padding: 8px;
                color: #495057;
            }
            QComboBox, QDateEdit {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                min-width: 150px;
            }
            QComboBox:focus, QDateEdit:focus {
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

    def load_employees(self):
        """Load employees into combo box (manager only)"""
        employees = self.db_manager.get_employees()
        for employee in employees:
            self.employee_combo.addItem(
                employee['name'],
                employee['id']
            )

    @Slot(str)
    def update_date_range(self, period):
        """Update date range based on selected period"""
        today = QDate.currentDate()
        
        if period == "Today":
            self.start_date.setDate(today)
            self.end_date.setDate(today)
        
        elif period == "This Week":
            self.start_date.setDate(today.addDays(-today.dayOfWeek() + 1))
            self.end_date.setDate(today)
        
        elif period == "This Month":
            self.start_date.setDate(QDate(today.year(), today.month(), 1))
            self.end_date.setDate(today)
        
        elif period == "Last 30 Days":
            self.start_date.setDate(today.addDays(-30))
            self.end_date.setDate(today)

    def load_reports(self):
        """Load reports into table based on filters"""
        # Get filter values
        start_date = self.start_date.date().toPython()
        end_date = self.end_date.date().toPython()
        status = self.status_combo.currentText()
        
        # Get employee ID filter (managers only)
        employee_id = None
        if self.user_data['role'] == 'manager' and \
           self.employee_combo.currentText() != "All Employees":
            employee_id = self.employee_combo.currentData()
        
        # If not manager, always filter by current employee
        if self.user_data['role'] != 'manager':
            employee_id = self.user_data['id']

        # Get contacts
        contacts = self.db_manager.get_employee_contacts(
            employee_id if employee_id else self.user_data['id'],
            self.user_data['role'] == 'manager',
            start_date
        )

        # Filter contacts
        filtered_contacts = [
            c for c in contacts
            if start_date <= c['contact_datetime'].date() <= end_date
            and (status == "All Status" or c['status'] == status)
        ]

        # Update table
        self.report_table.setRowCount(len(filtered_contacts))
        
        for row, contact in enumerate(filtered_contacts):
            # Date/Time
            dt = contact['contact_datetime'].strftime("%Y-%m-%d %H:%M")
            self.report_table.setItem(row, 0, QTableWidgetItem(dt))
            
            # Client Name
            self.report_table.setItem(
                row, 1, QTableWidgetItem(contact['client_name'])
            )
            
            # Client Type
            self.report_table.setItem(
                row, 2, QTableWidgetItem(contact['client_type'])
            )
            
            # Employee
            self.report_table.setItem(
                row, 3, QTableWidgetItem(contact['employee_name'])
            )
            
            # Method
            self.report_table.setItem(
                row, 4, QTableWidgetItem(contact['contact_method'])
            )
            
            # Rating
            rating = str(contact['conversion_rating']) if contact['conversion_rating'] else ""
            self.report_table.setItem(row, 5, QTableWidgetItem(rating))
            
            # Status
            self.report_table.setItem(
                row, 6, QTableWidgetItem(contact['status'])
            )

        # Update summary
        total_contacts = len(filtered_contacts)
        self.total_label.setText(f"Total Contacts: {total_contacts}")

        # Calculate average rating
        ratings = [c['conversion_rating'] for c in filtered_contacts 
                  if c['conversion_rating']]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        self.rating_label.setText(
            f"Average Rating: {avg_rating:.1f}"
        )

        # Calculate completion rate
        completed = sum(1 for c in filtered_contacts 
                       if c['status'] == 'Completed')
        completion_rate = (completed / total_contacts * 100) if total_contacts else 0
        self.completion_label.setText(
            f"Completion Rate: {completion_rate:.1f}%"
        )
