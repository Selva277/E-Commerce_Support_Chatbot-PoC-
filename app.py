# app.py - Flask Backend with Gemini LLM and MySQL

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import google.generativeai as genai
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')  # Use appropriate Gemini model

# MySQL Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME', 'ecommerce_support')
}

# Knowledge Base for RAG
KNOWLEDGE_BASE = {
    'return_policy': 'You can return items within 30 days of delivery. Items must be unused and in original packaging. Visit our Returns page or contact support with your order number.',
    'shipping_options': 'We offer Standard (5-7 days, $5), Express (2-3 days, $15), and Overnight shipping ($25). Shipping costs may vary by location.',
    'payment_methods': 'We accept all major credit cards (Visa, Mastercard, Amex), debit cards, PayPal, Apple Pay, and Google Pay.',
    'track_order': 'You can track your order using your order number. Provide your order number and I will check the current status.',
    'cancel_order': 'Orders can be cancelled within 24 hours of placement if they haven\'t shipped yet. After shipping, you\'ll need to initiate a return.',
    'customer_support': 'Our customer support team is available 24/7. Email: support@ecommerce.com | Phone: 1-800-SUPPORT',
    'warranty': 'All products come with a 1-year manufacturer warranty. Extended warranties are available at checkout.',
    'refund_process': 'Refunds are processed within 5-7 business days after we receive your returned item. You\'ll receive an email confirmation.'
}

# Database Helper Functions
def get_db_connection():
    """Create database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def query_order(order_id):
    """Query order from database"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT o.*, u.name, u.email 
            FROM orders o 
            JOIN users u ON o.user_id = u.user_id 
            WHERE o.order_id = %s
        """
        cursor.execute(query, (order_id,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result
    except Error as e:
        print(f"Error querying order: {e}")
        return None

def query_user_orders(user_id):
    """Query all orders for a user"""
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM orders WHERE user_id = %s ORDER BY order_date DESC"
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return results
    except Error as e:
        print(f"Error querying user orders: {e}")
        return []

def create_ticket(user_id, issue_description):
    """Create support ticket"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor()
        query = """
            INSERT INTO tickets (user_id, issue_description, status, created_date) 
            VALUES (%s, %s, 'open', %s)
        """
        cursor.execute(query, (user_id, issue_description, datetime.now()))
        connection.commit()
        ticket_id = cursor.lastrowid
        cursor.close()
        connection.close()
        return ticket_id
    except Error as e:
        print(f"Error creating ticket: {e}")
        return None

# RAG Helper Functions
def retrieve_from_knowledge_base(query):
    """Retrieve relevant information from knowledge base"""
    query_lower = query.lower()
    relevant_info = []
    
    for key, value in KNOWLEDGE_BASE.items():
        # Check if any keyword matches
        keywords = key.split('_')
        if any(keyword in query_lower for keyword in keywords):
            relevant_info.append(value)
    
    return relevant_info

def detect_intent(query):
    """Detect user intent from query"""
    query_lower = query.lower()
    
    # Order tracking
    if any(word in query_lower for word in ['order', 'track', 'status', 'where is', 'delivery']):
        return 'track_order'
    
    # Returns
    if any(word in query_lower for word in ['return', 'refund', 'send back']):
        return 'return_item'
    
    # Shipping
    if any(word in query_lower for word in ['shipping', 'ship', 'delivery options']):
        return 'shipping_info'
    
    # Payment
    if any(word in query_lower for word in ['payment', 'pay', 'card', 'paypal']):
        return 'payment_info'
    
    # Cancel
    if any(word in query_lower for word in ['cancel', 'stop']):
        return 'cancel_order'
    
    # Address change
    if 'address' in query_lower and 'change' in query_lower:
        return 'change_address'
    
    return 'general'

def extract_order_number(query):
    """Extract order number from query"""
    import re
    # Look for 5-digit numbers
    match = re.search(r'\b\d{5}\b', query)
    return match.group(0) if match else None

def generate_gemini_response(query, context, db_info=None, kb_info=None):
    """Generate response using Gemini LLM"""
    
    # Build prompt with context
    prompt = f"""You are a helpful e-commerce customer support assistant. 
    
User Query: {query}

"""
    
    if db_info:
        prompt += f"\nDatabase Information: {json.dumps(db_info, default=str)}\n"
    
    if kb_info:
        prompt += f"\nKnowledge Base Information: {' '.join(kb_info)}\n"
    
    prompt += """
Please provide a helpful, concise, and friendly response. If you're providing order information, be specific.
If you need more information from the user, ask clearly. Keep responses under 3 sentences unless providing detailed information.
"""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating Gemini response: {e}")
        return "I apologize, but I'm having trouble processing your request. Please try again or contact our support team."

# API Routes
@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    data = request.json
    user_message = data.get('message', '')
    conversation_context = data.get('context', {})
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Detect intent
    intent = detect_intent(user_message)
    
    # Initialize response data
    response_data = {
        'message': '',
        'type': 'general',
        'needs_escalation': False,
        'context': conversation_context
    }
    
    # RAG Pipeline: Step 1 - Database Retrieval
    if intent == 'track_order':
        order_num = extract_order_number(user_message)
        
        if order_num:
            order = query_order(order_num)
            if order:
                # Generate response using Gemini with database info
                gemini_response = generate_gemini_response(
                    user_message, 
                    conversation_context, 
                    db_info=order
                )
                response_data['message'] = gemini_response
                response_data['type'] = 'database_response'
                response_data['order_info'] = order
            else:
                response_data['message'] = f"I couldn't find order #{order_num} in our system. Please verify the order number or contact support."
                response_data['type'] = 'error'
                response_data['needs_escalation'] = True
        else:
            # Ask for order number
            if conversation_context.get('awaiting_order_number'):
                response_data['message'] = "I need a valid 5-digit order number. Could you please provide it?"
                response_data['type'] = 'clarification'
            else:
                response_data['message'] = "I can help you track your order! Could you please provide your order number?"
                response_data['type'] = 'clarification'
                response_data['context']['awaiting_order_number'] = True
    
    # RAG Pipeline: Step 2 - Knowledge Base Retrieval
    elif intent in ['return_item', 'shipping_info', 'payment_info', 'cancel_order']:
        kb_info = retrieve_from_knowledge_base(user_message)
        if kb_info:
            # Generate response using Gemini with knowledge base info
            gemini_response = generate_gemini_response(
                user_message, 
                conversation_context, 
                kb_info=kb_info
            )
            response_data['message'] = gemini_response
            response_data['type'] = 'knowledge_base_response'
        else:
            # Fallback to pure Gemini generation
            gemini_response = generate_gemini_response(user_message, conversation_context)
            response_data['message'] = gemini_response
            response_data['type'] = 'generated_response'
    
    # RAG Pipeline: Step 3 - Escalation needed
    elif intent == 'change_address':
        response_data['message'] = "I understand you want to change your shipping address. I cannot modify addresses directly, but I can create a support ticket for our team to help you immediately. Would you like me to do that?"
        response_data['type'] = 'escalation'
        response_data['needs_escalation'] = True
    
    # RAG Pipeline: Step 4 - General/Fallback
    else:
        # Try knowledge base first
        kb_info = retrieve_from_knowledge_base(user_message)
        gemini_response = generate_gemini_response(
            user_message, 
            conversation_context, 
            kb_info=kb_info if kb_info else None
        )
        response_data['message'] = gemini_response
        response_data['type'] = 'generated_response' if kb_info else 'fallback'
    
    return jsonify(response_data)

@app.route('/api/create_ticket', methods=['POST'])
def create_support_ticket():
    """Create a support ticket"""
    data = request.json
    user_id = data.get('user_id', 1)  # Default user for demo
    issue = data.get('issue', '')
    
    ticket_id = create_ticket(user_id, issue)
    
    if ticket_id:
        return jsonify({
            'success': True,
            'ticket_id': ticket_id,
            'message': f'Support ticket #{ticket_id} has been created. Our team will contact you within 24 hours.'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Failed to create ticket. Please try again.'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)