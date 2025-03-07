from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Employee:
    id: Optional[int]
    name: str
    login_id: str
    role: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Client:
    id: Optional[int]
    name: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    state_code: Optional[str]
    client_type: str  # 'client' or 'potential'
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Contact:
    id: Optional[int]
    client_id: int
    employee_id: int
    contact_datetime: datetime
    contact_method: str  # 'phone', 'email', 'in-person', 'other'
    conversion_rating: Optional[int]
    notes: Optional[str]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class StateCode:
    code: str
    description: str
