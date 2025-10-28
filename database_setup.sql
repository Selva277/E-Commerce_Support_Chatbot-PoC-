-- database_setup.sql
-- MySQL Database Setup for E-commerce Support Chatbot

-- Create database
CREATE DATABASE IF NOT EXISTS ecommerce_support;
USE ecommerce_support;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email)
);

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(10) PRIMARY KEY,
    user_id INT NOT NULL,
    status ENUM('processing', 'shipped', 'delivered', 'cancelled') DEFAULT 'processing',
    items TEXT NOT NULL,
    total_amount DECIMAL(10, 2),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estimated_delivery VARCHAR(50),
    tracking_number VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);

-- Create tickets table
CREATE TABLE IF NOT EXISTS tickets (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    issue_description TEXT NOT NULL,
    status ENUM('open', 'in_progress', 'resolved', 'closed') DEFAULT 'open',
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_date TIMESTAMP NULL,
    assigned_agent VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);

-- Create conversation_history table (optional - for tracking chats)
CREATE TABLE IF NOT EXISTS conversation_history (
    conversation_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    user_message TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    intent VARCHAR(50),
    response_type VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_user_id (user_id),
    INDEX idx_timestamp (timestamp)
);

-- Insert sample users
INSERT INTO users (name, email, phone) VALUES
('John Doe', 'john@example.com', '+1-555-0101'),
('Jane Smith', 'jane@example.com', '+1-555-0102'),
('Bob Johnson', 'bob@example.com', '+1-555-0103'),
('Alice Williams', 'alice@example.com', '+1-555-0104');

-- Insert sample orders
INSERT INTO orders (order_id, user_id, status, items, total_amount, order_date, estimated_delivery, tracking_number) VALUES
('12345', 1, 'shipped', 'Running Shoes - Nike Air Max', 129.99, '2025-10-20 10:30:00', '3 days', 'TRK123456789'),
('12346', 1, 'processing', 'T-Shirt - Adidas Classic', 29.99, '2025-10-25 14:20:00', '5 days', NULL),
('12347', 2, 'delivered', 'Laptop - Dell XPS 13', 1299.99, '2025-10-15 09:15:00', 'delivered', 'TRK987654321'),
('12348', 2, 'shipped', 'Wireless Mouse - Logitech MX', 79.99, '2025-10-24 16:45:00', '2 days', 'TRK456789123'),
('12349', 3, 'processing', 'Headphones - Sony WH-1000XM4', 349.99, '2025-10-26 11:00:00', '4 days', NULL),
('12350', 4, 'cancelled', 'Smart Watch - Apple Watch', 399.99, '2025-10-18 13:30:00', 'cancelled', NULL);

-- Insert sample tickets
INSERT INTO tickets (user_id, issue_description, status, created_date) VALUES
(1, 'Wrong item received - ordered blue shoes, got red ones', 'open', '2025-10-22 10:00:00'),
(2, 'Package was damaged during delivery', 'in_progress', '2025-10-21 15:30:00'),
(3, 'Want to change shipping address for order 12349', 'open', '2025-10-26 12:00:00');

-- Create view for order details with user info
CREATE OR REPLACE VIEW order_details_view AS
SELECT 
    o.order_id,
    o.status,
    o.items,
    o.total_amount,
    o.order_date,
    o.estimated_delivery,
    o.tracking_number,
    u.name AS customer_name,
    u.email AS customer_email,
    u.phone AS customer_phone
FROM orders o
JOIN users u ON o.user_id = u.user_id;

-- Verify data
SELECT 'Users Table' as 'Table';
SELECT * FROM users;

SELECT 'Orders Table' as 'Table';
SELECT * FROM orders;

SELECT 'Tickets Table' as 'Table';
SELECT * FROM tickets;