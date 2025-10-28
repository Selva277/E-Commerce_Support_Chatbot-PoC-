# E-commerce Support Chatbot

A complete **Retrieval-Augmented Generation (RAG)** powered customer support chatbot built with Python Flask, Google Gemini AI, MySQL, and modern HTML/CSS/JavaScript.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)
![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-purple.svg)

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Demo](#demo)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)

## ✨ Features

### 🧠 RAG Pipeline
- **Database Retrieval**: Real-time queries from MySQL for orders, users, and tickets
- **Knowledge Base**: FAQ retrieval for common questions (with Indian Rupee pricing)
- **AI Generation**: Google Gemini 2.5 Flash for natural language responses
- **Smart Escalation**: Graceful fallback to human support when needed

### 💬 Conversational AI
- Natural language understanding with context-aware intent detection
- Multi-turn conversation support with state management
- Automatic order number extraction and validation
- Standalone order number handling
- Multi-source response generation

### 🗄️ Database Integration
- Real-time order tracking with status updates
- Customer information lookup
- Automated support ticket creation
- Conversation history logging
- Order status-based response formatting

### 🎨 Modern UI
- Clean, gradient-based design
- Real-time typing indicators
- Response source badges (Database/KB/AI/Escalation)
- Quick action buttons
- Fully responsive layout

## 🏗️ Architecture

```
┌─────────────┐
│   User      │
│  (Browser)  │
└──────┬──────┘
       │
       │ HTTP/JSON
       ↓
┌─────────────────────────────────────────┐
│          Flask Backend (app.py)         │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐   │
│  │      RAG Pipeline               │   │
│  ├─────────────────────────────────┤   │
│  │  1. Context-Aware State Check   │   │
│  │  2. Intent Detection            │   │
│  │  3. Database Retrieval          │───┼──→ MySQL
│  │  4. Knowledge Base Search       │   │
│  │  5. Gemini AI Generation        │───┼──→ Gemini 2.5 Flash API
│  │  6. Response Synthesis          │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
       │
       │ JSON Response
       ↓
┌─────────────┐
│  Frontend   │
│  (HTML/JS)  │
└─────────────┘
```

## 🎬 Demo

### Sample Conversations

**Order Tracking:**
```
User: Where is my order 12345?
Bot: Your order #12345 (Running Shoes - Nike Air Max) is on its way 
     and should arrive within 3 days. Tracking number: TRK123456789
     🗄️ From Database
```

**Standalone Order Number:**
```
User: 12345
Bot: Your order #12345 (Running Shoes - Nike Air Max) is on its way 
     and should arrive within 3 days.
     🗄️ From Database
```

**Context-Aware Return Flow:**
```
User: I want to return an item
Bot: I can help you with a return! Please provide your 5-digit order number.

User: 12347
Bot: I found your order #12347 (Laptop - Dell XPS 13). You can return it 
     within 30 days. Visit our Returns page: https://ecommerce.com/returns. 
     Need help with the process?
     🗄️ From Database
```

**Return Policy:**
```
User: How do I return an item?
Bot: You can return items within 30 days of delivery. Items must 
     be unused and in original packaging. Visit our Returns page 
     or contact support with your order number.
     📚 Knowledge Base
```

**Cancellation Flow:**
```
User: Cancel order 12346
Bot: I've created a cancellation request for order #12346 (T-Shirt - 
     Adidas Classic). Our team will process it within 24 hours. Your 
     ticket number is #4.
     ⚠️ Escalation
```

**Address Change:**
```
User: Change address for 12345
Bot: Order #12345 (Running Shoes - Nike Air Max) has already shipped. 
     The address cannot be changed now. You may need to contact the 
     carrier or wait for delivery.
     🗄️ From Database
```

## 📦 Prerequisites

- **Python 3.8+**
- **MySQL 8.0+**
- **Google Gemini API Key** ([Get one here](https://makersuite.google.com/app/apikey))
- **pip** (Python package manager)
- **Modern web browser** (Chrome, Firefox, Safari, Edge)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ecommerce-chatbot.git
cd ecommerce-chatbot
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup MySQL Database

```bash
# Start MySQL server (if not running)
# Windows: Start MySQL service from Services
# Mac: brew services start mysql
# Linux: sudo systemctl start mysql

# Create database and tables
mysql -u root -p < database_setup.sql
```

### 5. Create Templates Folder

```bash
# Windows
mkdir templates
move index.html templates\

# Mac/Linux
mkdir -p templates
mv index.html templates/
```

## ⚙️ Configuration

### 1. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=ecommerce_support

# Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here
```

**Important:** Never commit `.env` file to version control. Use `.env.example` as a template.

### 2. Configure Database (Alternative)

If not using `.env`, edit `app.py` (lines 26-31):

```python
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD'),  # ← Change this
    'database': os.getenv('DB_NAME', 'ecommerce_support')
}
```

### 3. Configure Gemini API

The API is configured via environment variables. Add your key to `.env`:

```env
GEMINI_API_KEY=AIzaSy...your_actual_key
```

Get your API key from: [Google AI Studio](https://makersuite.google.com/app/apikey)

**Note:** The app uses `gemini-2.5-flash` model for faster and more efficient responses.

### 4. Verify Setup

Run the setup checker:

```bash
# Detailed check
python check_setup.py

# Quick check (Windows only)
check_setup.bat
```

This will verify all configurations and dependencies.

## 🎮 Usage

### Start the Application

```bash
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### Open in Browser

Navigate to: **http://localhost:5000**

### Try Sample Queries

1. **Track Order**: "Where is my order 12345?" or just "12345"
2. **Returns**: "How do I return an item?" or "Return order 12347"
3. **Shipping**: "What are the shipping options?"
4. **Payments**: "What payment methods do you accept?"
5. **Cancel**: "Cancel order 12346"
6. **Address Change**: "Change address for order 12349"

### Sample Test Orders

The database comes pre-populated with these test orders:

| Order ID | Status | Items | Notes |
|----------|--------|-------|-------|
| 12345 | shipped | Running Shoes - Nike Air Max | Has tracking number |
| 12346 | processing | T-Shirt - Adidas Classic | Can be cancelled |
| 12347 | delivered | Laptop - Dell XPS 13 | Can be returned |
| 12348 | shipped | Wireless Mouse - Logitech MX | In transit |
| 12349 | processing | Headphones - Sony WH-1000XM4 | Can modify address |
| 12350 | cancelled | Smart Watch - Apple Watch | Already cancelled |

## 📁 Project Structure

```
ecommerce-chatbot/
│
├── app.py                      # Flask backend with RAG pipeline
├── database_setup.sql          # MySQL database schema & sample data
├── requirements.txt            # Python dependencies
├── check_setup.py             # Setup verification script
├── check_setup.bat            # Windows quick checker
├── .env                       # Environment variables (create this)
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore file
├── README.md                  # This file
├── LICENSE                    # MIT License
│
└── templates/
    └── index.html             # Frontend UI (HTML/CSS/JS)
```

## 📡 API Documentation

### POST `/api/chat`

Send a message to the chatbot with conversation context.

**Request:**
```json
{
  "message": "Where is my order 12345?",
  "context": {}
}
```

**Response:**
```json
{
  "message": "Your order #12345 (Running Shoes - Nike Air Max) is on its way and should arrive within 3 days. Tracking number: TRK123456789",
  "type": "database_response",
  "needs_escalation": false,
  "context": {},
  "order_info": {
    "order_id": "12345",
    "status": "shipped",
    "items": "Running Shoes - Nike Air Max",
    "estimated_delivery": "3 days",
    "tracking_number": "TRK123456789"
  }
}
```

**Response Types:**
- `database_response` - Retrieved from MySQL database
- `knowledge_base_response` - Retrieved from knowledge base
- `generated_response` - Generated by Gemini AI
- `escalation` - Needs human support (ticket creation offered)
- `escalation_confirmed` - Ticket created successfully
- `clarification` - Needs more information from user
- `error` - Error occurred

**Context Management:**

The chatbot maintains conversation state through context flags:

```json
{
  "context": {
    "awaiting_order_number": true,
    "awaiting_return_order_number": true,
    "awaiting_order_for_cancel": true,
    "awaiting_order_for_address": true,
    "awaiting_cancel_confirmation": true,
    "awaiting_address_change_confirmation": true,
    "pending_order_number": "12345"
  }
}
```

**Intent Detection:**

The system detects these intents:
- `track_order` - Order status inquiry
- `return_item` / `return_item_with_order` - Return requests
- `cancel_order` / `cancel_order_with_number` - Cancellation requests
- `change_address` / `change_address_with_number` - Address updates
- `shipping_info` - Shipping options query
- `payment_info` - Payment methods query
- `contact_support` - Customer support contact
- `general` - General queries handled by Gemini AI

### POST `/api/create_ticket`

Create a support ticket for escalation.

**Request:**
```json
{
  "user_id": 1,
  "issue": "Need to change shipping address for order #12349"
}
```

**Response:**
```json
{
  "success": true,
  "ticket_id": 4,
  "message": "Support ticket #4 has been created. Our team will contact you within 24 hours."
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Failed to create ticket. Please try again."
}
```

## 🧪 Testing

### Run Setup Checker

```bash
python check_setup.py
```

### Manual Testing

1. **Database Connection:**
```bash
mysql -u root -p
USE ecommerce_support;
SELECT * FROM orders;
SELECT * FROM users;
SELECT * FROM tickets;
```

2. **API Endpoints:**
```bash
# Test chat endpoint
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Where is my order 12345?", "context": {}}'

# Test ticket creation
curl -X POST http://localhost:5000/api/create_ticket \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "issue": "Test ticket"}'
```

### Test Scenarios

| Scenario | Query | Expected Response Type |
|----------|-------|----------------------|
| Order tracking | "Where is my order 12345?" | database_response |
| Standalone order | "12345" | database_response |
| Return with order | "Return order 12347" | database_response |
| Return without order | "I want to return an item" | clarification → database_response |
| Cancel processing order | "Cancel order 12346" | escalation_confirmed |
| Cancel shipped order | "Cancel order 12345" | database_response (cannot cancel) |
| Shipping info | "What are shipping options?" | knowledge_base_response |
| Payment methods | "What payment methods?" | knowledge_base_response |
| Address change | "Change address for 12349" | escalation |
| General query | "Tell me about your store" | generated_response |

## 🔧 Troubleshooting

### Environment Variables Not Loading

**Error:** `KeyError: 'GEMINI_API_KEY'`

**Solutions:**
- Create `.env` file in root directory
- Ensure `python-dotenv` is installed: `pip install python-dotenv`
- Verify `.env` file format (no spaces around `=`)

### MySQL Connection Error

**Error:** `Can't connect to MySQL server`

**Solutions:**
- Check if MySQL is running: `mysql -u root -p`
- Verify credentials in `.env` file
- Ensure database exists: `SHOW DATABASES LIKE 'ecommerce_support';`
- Check DB_PASSWORD is set correctly in `.env`

### Gemini API Error

**Error:** `Invalid API key` or `API key not configured`

**Solutions:**
- Verify API key in `.env` file
- Ensure key starts with `AIzaSy`
- Get new key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- Check rate limits and quotas

### Module Not Found

**Error:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
```bash
pip install -r requirements.txt
```

### Port Already in Use

**Error:** `Address already in use`

**Solutions:**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:5000 | xargs kill -9
```

### Templates Not Found

**Error:** `TemplateNotFound: index.html`

**Solution:**
```bash
# Create templates folder and move index.html
mkdir templates
mv index.html templates/
```

### Order Not Found

**Error:** "I couldn't find order #XXXXX"

**Verify:**
- Order number is exactly 5 digits
- Order exists in database: `SELECT * FROM orders WHERE order_id = 'XXXXX';`
- Use sample orders: 12345, 12346, 12347, 12348, 12349, 12350

## 🗃️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email)
);
```

### Orders Table
```sql
CREATE TABLE orders (
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
```

### Tickets Table
```sql
CREATE TABLE tickets (
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
```

### Conversation History Table
```sql
CREATE TABLE conversation_history (
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
```

## 💡 Key Features Explained

### Context-Aware Conversations

The chatbot maintains conversation state to handle multi-turn interactions:

```python
# Example: Return flow
User: "I want to return an item"
Bot: Sets awaiting_return_order_number = True
Bot: "Please provide your 5-digit order number"

User: "12347"
Bot: Detects context, treats as order number
Bot: Queries database and provides return info
```

### Standalone Order Number Handling

The bot intelligently handles bare order numbers based on context:

```python
User: "12345"  # No other text

# Context determines action:
- Default: Track order
- In return flow: Process return
- In cancel flow: Cancel order
- In address flow: Update address
```

### Smart Intent Detection

Uses pattern matching and context awareness:

```python
detect_intent(query, context):
    - Checks for standalone order numbers
    - Detects keywords (return, track, cancel, etc.)
    - Considers conversation context
    - Returns appropriate intent
```

### Order Status-Based Responses

Responses adapt to order status:

- **Processing**: Can cancel, can't return yet
- **Shipped**: Can't cancel, can't change address, can return later
- **Delivered**: Can return within 30 days
- **Cancelled**: No actions needed

## 🌟 Advanced Usage

### Custom Knowledge Base

Add entries to `KNOWLEDGE_BASE` in `app.py`:

```python
KNOWLEDGE_BASE = {
    'your_key': 'Your custom information here',
    'warranty': 'All products come with a 1-year manufacturer warranty.',
    # Add more...
}
```

### Custom Intents

Add new intents in `detect_intent()` function:

```python
# Example: Product inquiry
if any(word in query_lower for word in ['product', 'item', 'catalog']):
    return 'product_inquiry'
```

### Extending Database Queries

Add new query functions:

```python
def query_product(product_id):
    """Query product from database"""
    connection = get_db_connection()
    # Your implementation
```

## 📝 Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DB_HOST` | MySQL host | `localhost` |
| `DB_USER` | MySQL username | `root` |
| `DB_PASSWORD` | MySQL password | `your_password` |
| `DB_NAME` | Database name | `ecommerce_support` |
| `GEMINI_API_KEY` | Google Gemini API key | `AIzaSy...` |
