# E-commerce Support Chatbot

A complete **Retrieval-Augmented Generation (RAG)** powered customer support chatbot built with Python Flask, Google Gemini AI, MySQL, and modern HTML/CSS/JavaScript.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)
![Gemini](https://img.shields.io/badge/Gemini-AI-purple.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

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
- **Knowledge Base**: FAQ retrieval for common questions
- **AI Generation**: Google Gemini AI for natural language responses
- **Smart Escalation**: Graceful fallback to human support when needed

### 💬 Conversational AI
- Natural language understanding with intent detection
- Context-aware responses across multiple turns
- Order number extraction and validation
- Multi-source response generation

### 🗄️ Database Integration
- Real-time order tracking
- Customer information lookup
- Support ticket creation
- Conversation history logging

### 🎨 Modern UI
- Clean, gradient-based design
- Real-time typing indicators
- Response source badges (Database/KB/AI)
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
│  │  1. Intent Detection            │   │
│  │  2. Database Retrieval          │───┼──→ MySQL
│  │  3. Knowledge Base Search       │   │
│  │  4. Gemini AI Generation        │───┼──→ Gemini API
│  │  5. Response Synthesis          │   │
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
Bot: Your order #12345 containing "Running Shoes - Nike Air Max" 
     is currently shipped. It should arrive within 3 days.
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

**Escalation:**
```
User: Can I change my shipping address?
Bot: I understand you want to change your shipping address. I cannot 
     modify addresses directly, but I can create a support ticket for 
     our team to help you immediately. Would you like me to do that?
     ⚠️ Escalation
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

### 1. Configure Database

Edit `app.py` (lines 18-23):

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_mysql_password',  # ← Change this
    'database': 'ecommerce_support'
}
```

### 2. Configure Gemini API

Edit `app.py` (line 14):

```python
genai.configure(api_key='YOUR_GEMINI_API_KEY')  # ← Add your API key
```

Get your API key from: [Google AI Studio](https://makersuite.google.com/app/apikey)

### 3. Verify Setup

Run the setup checker:

```bash
python check_setup.py
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

1. **Track Order**: "Where is my order 12345?"
2. **Returns**: "How do I return an item?"
3. **Shipping**: "What are the shipping options?"
4. **Payments**: "What payment methods do you accept?"

## 📁 Project Structure

```
ecommerce-chatbot/
│
├── app.py                      # Flask backend with RAG pipeline
├── database_setup.sql          # MySQL database schema & sample data
├── requirements.txt            # Python dependencies
├── check_setup.py             # Setup verification script
├── check_setup.bat            # Windows quick checker
├── README.md                  # This file
├── .gitignore                 # Git ignore file
├── LICENSE                    # MIT License
│
└── templates/
    └── index.html             # Frontend UI (HTML/CSS/JS)
```

## 📡 API Documentation

### POST `/api/chat`

Send a message to the chatbot.

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
  "message": "Your order #12345 is shipped and will arrive in 3 days.",
  "type": "database_response",
  "needs_escalation": false,
  "context": {},
  "order_info": {
    "order_id": "12345",
    "status": "shipped",
    "items": "Running Shoes - Nike Air Max",
    "estimated_delivery": "3 days"
  }
}
```

**Response Types:**
- `database_response` - Retrieved from MySQL database
- `knowledge_base_response` - Retrieved from knowledge base
- `generated_response` - Generated by Gemini AI
- `escalation` - Needs human support
- `clarification` - Needs more information
- `error` - Error occurred

### POST `/api/create_ticket`

Create a support ticket.

**Request:**
```json
{
  "user_id": 1,
  "issue": "Need to change shipping address"
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
```

2. **API Endpoints:**
```bash
# Test chat endpoint
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Where is my order 12345?", "context": {}}'
```

### Test Queries

| Query | Expected Response Type |
|-------|----------------------|
| "Where is my order 12345?" | Database retrieval |
| "How do I return an item?" | Knowledge base |
| "What payment methods?" | Knowledge base |
| "Change my address" | Escalation |
| Random text | AI generation |

## 🔧 Troubleshooting

### MySQL Connection Error

**Error:** `Can't connect to MySQL server`

**Solutions:**
- Check if MySQL is running: `mysql -u root -p`
- Verify credentials in `app.py`
- Ensure database exists: `SHOW DATABASES LIKE 'ecommerce_support';`

### Gemini API Error

**Error:** `Invalid API key`

**Solutions:**
- Verify API key in `app.py`
- Get new key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- Check rate limits

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

## 🗃️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Orders Table
```sql
CREATE TABLE orders (
    order_id VARCHAR(10) PRIMARY KEY,
    user_id INT NOT NULL,
    status ENUM('processing', 'shipped', 'delivered', 'cancelled'),
    items TEXT NOT NULL,
    total_amount DECIMAL(10, 2),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estimated_delivery VARCHAR(50),
    tracking_number VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### Tickets Table
```sql
CREATE TABLE tickets (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    issue_description TEXT NOT NULL,
    status ENUM('open', 'in_progress', 'resolved', 'closed'),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```