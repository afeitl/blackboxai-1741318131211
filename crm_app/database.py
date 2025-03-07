import mysql.connector
from mysql.connector import Error
import bcrypt
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, host: str = 'localhost', database: str = 'crm_db',
                 user: str = 'root', password: str = ''):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None

    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            return True
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            return False

    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def verify_login(self, login_id: str, password: str) -> Optional[dict]:
        """Verify user login credentials"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT id, name, login_id, password_hash, role 
                FROM employees 
                WHERE login_id = %s
            """
            cursor.execute(query, (login_id,))
            user = cursor.fetchone()
            cursor.close()

            if user and bcrypt.checkpw(password.encode('utf-8'), 
                                     user['password_hash'].encode('utf-8')):
                return {
                    'id': user['id'],
                    'name': user['name'],
                    'login_id': user['login_id'],
                    'role': user['role']
                }
            return None
        except Error as e:
            logger.error(f"Error verifying login: {e}")
            return None

    def get_state_codes(self) -> List[Dict[str, str]]:
        """Get all state codes"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT code, description FROM state_codes ORDER BY description")
            states = cursor.fetchall()
            cursor.close()
            return states
        except Error as e:
            logger.error(f"Error fetching state codes: {e}")
            return []

    def create_client(self, client_data: Dict[str, Any]) -> Optional[int]:
        """Create a new client"""
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO clients (name, email, phone, address, state_code, client_type)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (
                client_data['name'],
                client_data.get('email'),
                client_data.get('phone'),
                client_data.get('address'),
                client_data.get('state_code'),
                client_data['client_type']
            )
            cursor.execute(query, values)
            self.connection.commit()
            client_id = cursor.lastrowid
            cursor.close()
            return client_id
        except Error as e:
            logger.error(f"Error creating client: {e}")
            return None

    def get_clients(self, search_term: str = "") -> List[Dict[str, Any]]:
        """Get all clients, optionally filtered by search term"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            if search_term:
                query = """
                    SELECT c.*, s.description as state_name 
                    FROM clients c
                    LEFT JOIN state_codes s ON c.state_code = s.code
                    WHERE c.name LIKE %s OR c.email LIKE %s
                    ORDER BY c.name
                """
                search_pattern = f"%{search_term}%"
                cursor.execute(query, (search_pattern, search_pattern))
            else:
                query = """
                    SELECT c.*, s.description as state_name 
                    FROM clients c
                    LEFT JOIN state_codes s ON c.state_code = s.code
                    ORDER BY c.name
                """
                cursor.execute(query)
            
            clients = cursor.fetchall()
            cursor.close()
            return clients
        except Error as e:
            logger.error(f"Error fetching clients: {e}")
            return []

    def create_contact(self, contact_data: Dict[str, Any]) -> Optional[int]:
        """Create a new contact record"""
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO contacts 
                (client_id, employee_id, contact_datetime, contact_method, 
                 conversion_rating, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (
                contact_data['client_id'],
                contact_data['employee_id'],
                contact_data['contact_datetime'],
                contact_data['contact_method'],
                contact_data.get('conversion_rating'),
                contact_data.get('notes')
            )
            cursor.execute(query, values)
            self.connection.commit()
            contact_id = cursor.lastrowid
            cursor.close()
            return contact_id
        except Error as e:
            logger.error(f"Error creating contact: {e}")
            return None

    def get_employee_contacts(self, employee_id: int, is_manager: bool = False,
                            start_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get contacts for an employee or all contacts for managers"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT c.*, cl.name as client_name, cl.client_type,
                       e.name as employee_name
                FROM contacts c
                JOIN clients cl ON c.client_id = cl.id
                JOIN employees e ON c.employee_id = e.id
            """
            params = []

            if not is_manager:
                query += " WHERE c.employee_id = %s"
                params.append(employee_id)

            if start_date:
                query += " AND c.contact_datetime >= %s" if params else " WHERE c.contact_datetime >= %s"
                params.append(start_date)

            query += " ORDER BY c.contact_datetime"
            
            cursor.execute(query, params)
            contacts = cursor.fetchall()
            cursor.close()
            return contacts
        except Error as e:
            logger.error(f"Error fetching contacts: {e}")
            return []

    def create_employee(self, employee_data: Dict[str, Any]) -> Optional[int]:
        """Create a new employee"""
        try:
            cursor = self.connection.cursor()
            # Hash the password
            password_hash = bcrypt.hashpw(
                employee_data['password'].encode('utf-8'),
                bcrypt.gensalt()
            )
            
            query = """
                INSERT INTO employees (name, login_id, password_hash, role)
                VALUES (%s, %s, %s, %s)
            """
            values = (
                employee_data['name'],
                employee_data['login_id'],
                password_hash,
                employee_data['role']
            )
            cursor.execute(query, values)
            self.connection.commit()
            employee_id = cursor.lastrowid
            cursor.close()
            return employee_id
        except Error as e:
            logger.error(f"Error creating employee: {e}")
            return None

    def get_employees(self) -> List[Dict[str, Any]]:
        """Get all employees"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT id, name, login_id, role, created_at, updated_at
                FROM employees
                ORDER BY name
            """
            cursor.execute(query)
            employees = cursor.fetchall()
            cursor.close()
            return employees
        except Error as e:
            logger.error(f"Error fetching employees: {e}")
            return []
