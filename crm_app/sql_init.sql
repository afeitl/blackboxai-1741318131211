-- Drop tables if they exist (for development purposes)
DROP TABLE IF EXISTS contacts;
DROP TABLE IF EXISTS clients;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS state_codes;

-- Create state_codes table
CREATE TABLE state_codes (
    code VARCHAR(2) PRIMARY KEY,
    description VARCHAR(100) NOT NULL
);

-- Create employees table
CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    login_id VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('employee', 'manager') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
