# Business CRM Application

A comprehensive Customer Relationship Management (CRM) system built with Python, PySide6, and MySQL. This application helps businesses manage client relationships, track contacts, and monitor potential client conversions.

## Features

- **Client Management**: Track both clients and potential clients
- **Employee Management**: Manage employee accounts with role-based access
- **Contact Scheduling**: Schedule and track client interactions
- **Reporting**: View contact reports with role-based filtering
- **Secure Authentication**: Password-protected access with role-based permissions
- **Modern UI**: Clean, responsive interface built with PySide6

## Requirements

- Python 3.8 or higher
- MySQL 8.0 or higher
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd crm_app
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Set up the MySQL database:
```bash
mysql -u root -p
```

In the MySQL prompt:
```sql
CREATE DATABASE crm_db;
USE crm_db;
source sql_init.sql;
```

5. Configure database connection:
Edit the database connection parameters in `desktop_main.py` to match your MySQL configuration:
```python
self.db_manager = DatabaseManager(
    host='localhost',
    database='crm_db',
    user='your_username',
    password='your_password'
)
```

## Running the Application

1. Start the desktop application:
```bash
python desktop_main.py
```

2. Log in with the default admin account:
- Login ID: admin
- Password: admin123

## Usage

### Client Management
- Add, edit, and delete client records
- Track client status (client/potential)
- Store contact information and state/province

### Employee Management (Managers Only)
- Create and manage employee accounts
- Set employee roles (employee/manager)
- Secure password management

### Contact Scheduling
- Schedule client contacts
- Track contact method (phone, email, in-person)
- Record conversion ratings for potential clients
- Update contact status (scheduled, completed, cancelled)

### Reporting
- View contact schedules and history
- Filter by date range and status
- Role-based access (employees see their contacts, managers see all)
- Track conversion metrics and completion rates

## Security Features

- Secure password hashing using bcrypt
- Role-based access control
- Session management
- Input validation and sanitization

## Database Schema

The application uses the following tables:
- employees: Store employee information and credentials
- clients: Store client and potential client information
- contacts: Track client interactions and schedules
- state_codes: Reference table for state/province codes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your chosen license]

## Support

For support, please [contact information or issue tracker link]
