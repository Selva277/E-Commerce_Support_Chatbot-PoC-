from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import google.generativeai as genai
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import re

load_dotenv()

app = Flask(__name__)
CORS(app)

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME', 'ecommerce_support')
}

KNOWLEDGE_BASE = {
    'return_policy': 'You can return items within 30 days of delivery. Items must be unused and in original packaging. Visit our Returns page or contact support with your order number.',
    'shipping_options': 'We offer Standard (5-7 days, ₹400), Express (2-3 days, ₹1,200), and Overnight shipping (₹2,000). Shipping costs may vary by location.',
    'payment_methods': 'We accept all major credit cards (Visa, Mastercard, RuPay), debit cards, UPI, Net Banking, Paytm, Google Pay, and PhonePe.',
    'track_order': 'You can track your order using your order number. Provide your order number and I will check the current status.',
    'cancel_order': 'Orders can be cancelled within 24 hours of placement if they haven\'t shipped yet. After shipping, you\'ll need to initiate a return.',
    'customer_support': 'Our customer support team is available 24/7. Email: support@ecommerce.com | Phone: 1800-000-0000',
    'warranty': 'All products come with a 1-year manufacturer warranty. Extended warranties are available at checkout.',
    'refund_process': 'Refunds are processed within 5-7 business days after we receive your returned item. You\'ll receive an email confirmation.'
}


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

def retrieve_from_knowledge_base(query):
    """Retrieve relevant information from knowledge base"""
    query_lower = query.lower()
    relevant_info = []
    
    for key, value in KNOWLEDGE_BASE.items():
        keywords = key.split('_')
        if any(keyword in query_lower for keyword in keywords):
            relevant_info.append(value)
    
    return relevant_info

def extract_order_number(query):
    """Extract order number from query - looks for 5-digit numbers"""
    # First check if the entire message is just a number (standalone order number)
    query_stripped = query.strip()
    if query_stripped.isdigit() and len(query_stripped) == 5:
        return query_stripped
    
    # Otherwise look for 5-digit numbers in the text
    match = re.search(r'\b\d{5}\b', query)
    return match.group(0) if match else None

def is_standalone_order_number(query):
    """Check if message is just an order number"""
    query_stripped = query.strip()
    return query_stripped.isdigit() and len(query_stripped) == 5

def detect_intent(query, context):
    """Detect user intent from query with context awareness"""
    query_lower = query.lower().strip()
    
    # Check if it's a standalone order number
    if is_standalone_order_number(query):
        # Context determines what to do with the order number
        if context.get('awaiting_return_order_number'):
            return 'return_item_with_order'
        elif context.get('awaiting_order_for_cancel'):
            return 'cancel_order_with_number'
        elif context.get('awaiting_order_for_address'):
            return 'change_address_with_number'
        else:
            # Default: treat as tracking request
            return 'track_order'
    
    # Has order number in query
    has_order_number = extract_order_number(query) is not None
    
    # Return/Refund intent
    if any(word in query_lower for word in ['return', 'refund', 'send back']):
        if has_order_number:
            return 'return_item_with_order'
        return 'return_item'
    
    # Order tracking
    if any(word in query_lower for word in ['track', 'status', 'where is', 'where\'s', 'delivery', 'order']):
        if 'return' not in query_lower and 'refund' not in query_lower and 'cancel' not in query_lower:
            return 'track_order'
    
    # Shipping
    if any(word in query_lower for word in ['shipping', 'ship', 'delivery options', 'how long']):
        if 'track' not in query_lower and 'where' not in query_lower and not has_order_number:
            return 'shipping_info'
    
    # Payment
    if any(word in query_lower for word in ['payment', 'pay', 'card', 'upi', 'paytm']):
        return 'payment_info'
    
    # Cancel
    if any(word in query_lower for word in ['cancel', 'stop order']):
        return 'cancel_order'
    
    # Address change
    if 'address' in query_lower and ('change' in query_lower or 'update' in query_lower or 'modify' in query_lower):
        return 'change_address'
    
    # Contact/Support
    if any(word in query_lower for word in ['contact', 'support', 'help', 'speak to', 'talk to', 'agent']):
        return 'contact_support'
    
    return 'general'

def generate_gemini_response(query, context, db_info=None, kb_info=None):
    """Generate response using Gemini LLM"""
    
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
        return "I apologize, but I'm having trouble processing your request. Please try again or contact our support team at support@ecommerce.com"

def format_order_status_message(order):
    """Format order status message based on order data"""
    status = order['status']
    order_id = order['order_id']
    items = order.get('items', 'your order')
    
    if status == 'shipped':
        delivery = order.get('estimated_delivery', '3 days')
        tracking = order.get('tracking_number', '')
        msg = f"Your order #{order_id} ({items}) is on its way and should arrive within {delivery}."
        if tracking:
            msg += f" Tracking number: {tracking}"
        return msg
    elif status == 'processing':
        delivery = order.get('estimated_delivery', '5-7 days')
        return f"Your order #{order_id} ({items}) is currently being processed and will ship soon. Expected delivery: {delivery}."
    elif status == 'delivered':
        return f"Your order #{order_id} ({items}) has been delivered. If you have any issues, please let me know!"
    elif status == 'cancelled':
        return f"Order #{order_id} ({items}) has been cancelled. If you need assistance, please contact our support team."
    else:
        return f"Your order #{order_id} status: {status}."

# API Routes
@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint with enhanced conversational behavior"""
    data = request.json
    user_message = data.get('message', '').strip()
    conversation_context = data.get('context', {})
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Initialize response data
    response_data = {
        'message': '',
        'type': 'general',
        'needs_escalation': False,
        'context': conversation_context.copy()
    }
    
    # Extract order number once for reuse
    order_num = extract_order_number(user_message)
    
    # ========== CONTEXT-AWARE STATE HANDLING ==========
    
    # State: Awaiting order number for tracking
    if conversation_context.get('awaiting_order_number'):
        if order_num:
            order = query_order(order_num)
            if order:
                response_data['message'] = format_order_status_message(order)
                response_data['type'] = 'database_response'
                response_data['order_info'] = order
                response_data['context'].pop('awaiting_order_number', None)
            else:
                response_data['message'] = f"I couldn't find order #{order_num} in our system. Please double-check the order number. Valid orders in our system are: 12345, 12346, 12347, 12348, 12349, 12350."
                response_data['type'] = 'error'
                response_data['context'].pop('awaiting_order_number', None)
        else:
            response_data['message'] = "I need a valid 5-digit order number to track your order. Could you please provide it?"
            response_data['type'] = 'clarification'
        
        return jsonify(response_data)
    
    # State: Awaiting order number for return
    if conversation_context.get('awaiting_return_order_number'):
        if order_num:
            order = query_order(order_num)
            if order:
                if order['status'] == 'delivered':
                    response_data['message'] = f"I found your order #{order_num} ({order['items']}). You can return it within 30 days. Visit our Returns page: https://ecommerce.com/returns. Need help with the process?"
                    response_data['type'] = 'database_response'
                    response_data['order_info'] = order
                elif order['status'] == 'shipped':
                    response_data['message'] = f"Your order #{order_num} ({order['items']}) is currently in transit. Once delivered, you can return it within 30 days. Visit: https://ecommerce.com/returns"
                    response_data['type'] = 'database_response'
                elif order['status'] == 'cancelled':
                    response_data['message'] = f"Order #{order_num} has already been cancelled. No return is needed."
                    response_data['type'] = 'database_response'
                else:
                    response_data['message'] = f"Order #{order_num} ({order['items']}) is still being processed. You can cancel it instead of returning. Would you like to cancel?"
                    response_data['type'] = 'database_response'
                    response_data['context']['awaiting_cancel_confirmation'] = True
                    response_data['context']['pending_order_number'] = order_num
                
                response_data['context'].pop('awaiting_return_order_number', None)
            else:
                response_data['message'] = f"I couldn't find order #{order_num} in our system. Please verify the order number. You can find it in your order confirmation email."
                response_data['type'] = 'error'
                response_data['context'].pop('awaiting_return_order_number', None)
        else:
            response_data['message'] = "Please provide your 5-digit order number so I can help you with the return."
            response_data['type'] = 'clarification'
        
        return jsonify(response_data)
    
    # State: Awaiting order number for cancellation
    if conversation_context.get('awaiting_order_for_cancel'):
        if order_num:
            order = query_order(order_num)
            if order:
                if order['status'] == 'processing':
                    user_id = order['user_id']
                    issue_desc = f"Cancel order request: Order #{order_num} - {order['items']}"
                    ticket_id = create_ticket(user_id, issue_desc)
                    
                    if ticket_id:
                        response_data['message'] = f"I've created a cancellation request for order #{order_num} ({order['items']}). Our team will process it within 24 hours. Your ticket number is #{ticket_id}."
                        response_data['type'] = 'escalation_confirmed'
                        response_data['ticket_id'] = ticket_id
                    else:
                        response_data['message'] = "I'm sorry, I couldn't create the cancellation request. Please contact support@ecommerce.com or call 1800-000-0000."
                        response_data['type'] = 'error'
                elif order['status'] == 'shipped':
                    response_data['message'] = f"Order #{order_num} ({order['items']}) has already shipped. You'll need to refuse the delivery or initiate a return once received."
                    response_data['type'] = 'database_response'
                elif order['status'] == 'cancelled':
                    response_data['message'] = f"Order #{order_num} is already cancelled."
                    response_data['type'] = 'database_response'
                else:
                    response_data['message'] = f"Order #{order_num} status is '{order['status']}'. Please contact support for assistance."
                    response_data['type'] = 'database_response'
                
                response_data['context'].pop('awaiting_order_for_cancel', None)
            else:
                response_data['message'] = f"I couldn't find order #{order_num}. Please verify the order number."
                response_data['type'] = 'error'
                response_data['context'].pop('awaiting_order_for_cancel', None)
        else:
            response_data['message'] = "Please provide your 5-digit order number to cancel."
            response_data['type'] = 'clarification'
        
        return jsonify(response_data)
    
    # State: Awaiting order number for address change
    if conversation_context.get('awaiting_order_for_address'):
        if order_num:
            order = query_order(order_num)
            if order:
                if order['status'] == 'processing':
                    response_data['message'] = f"I found order #{order_num} ({order['items']}). I'll forward your address change request to our support team. Would you like me to create a ticket?"
                    response_data['type'] = 'escalation'
                    response_data['needs_escalation'] = True
                    response_data['context']['awaiting_address_change_confirmation'] = True
                    response_data['context']['pending_order_number'] = order_num
                    response_data['context'].pop('awaiting_order_for_address', None)
                elif order['status'] == 'shipped':
                    response_data['message'] = f"Order #{order_num} ({order['items']}) has already shipped. The address cannot be changed now. You may need to contact the carrier or wait for delivery."
                    response_data['type'] = 'database_response'
                    response_data['context'].pop('awaiting_order_for_address', None)
                else:
                    response_data['message'] = f"Order #{order_num} status is '{order['status']}'. Address changes may not be possible."
                    response_data['type'] = 'database_response'
                    response_data['context'].pop('awaiting_order_for_address', None)
            else:
                response_data['message'] = f"I couldn't find order #{order_num}. Please verify the order number."
                response_data['type'] = 'error'
                response_data['context'].pop('awaiting_order_for_address', None)
        else:
            response_data['message'] = "Please provide your 5-digit order number to update the address."
            response_data['type'] = 'clarification'
        
        return jsonify(response_data)
    
    # State: Awaiting address change confirmation
    if conversation_context.get('awaiting_address_change_confirmation'):
        order_num = conversation_context.get('pending_order_number')
        user_response_lower = user_message.lower()
        
        if any(word in user_response_lower for word in ['yes', 'sure', 'please', 'ok', 'yeah', 'yep', 'confirm']):
            order = query_order(order_num) if order_num else None
            user_id = order['user_id'] if order else 1
            issue_desc = f"Address change request for order #{order_num}"
            
            ticket_id = create_ticket(user_id, issue_desc)
            if ticket_id:
                response_data['message'] = f"I've created ticket #{ticket_id} for your address change request. Our support team will contact you shortly to update the delivery address."
                response_data['type'] = 'escalation_confirmed'
                response_data['ticket_id'] = ticket_id
            else:
                response_data['message'] = "I'm sorry, I couldn't create the ticket. Please contact support@ecommerce.com directly."
                response_data['type'] = 'error'
        else:
            response_data['message'] = "No problem! Is there anything else I can help you with?"
            response_data['type'] = 'general'
        
        response_data['context'].pop('awaiting_address_change_confirmation', None)
        response_data['context'].pop('pending_order_number', None)
        return jsonify(response_data)
    
    # State: Awaiting cancel confirmation
    if conversation_context.get('awaiting_cancel_confirmation'):
        order_num = conversation_context.get('pending_order_number')
        user_response_lower = user_message.lower()
        
        if any(word in user_response_lower for word in ['yes', 'sure', 'please', 'ok', 'yeah', 'yep', 'cancel']):
            order = query_order(order_num) if order_num else None
            if order:
                user_id = order['user_id']
                issue_desc = f"Cancel order request: Order #{order_num} - {order['items']}"
                ticket_id = create_ticket(user_id, issue_desc)
                
                if ticket_id:
                    response_data['message'] = f"I've created a cancellation request for order #{order_num}. Our team will process it within 24 hours. Ticket #{ticket_id}."
                    response_data['type'] = 'escalation_confirmed'
                    response_data['ticket_id'] = ticket_id
                else:
                    response_data['message'] = "I'm sorry, I couldn't create the request. Please contact support@ecommerce.com"
                    response_data['type'] = 'error'
        else:
            response_data['message'] = "Okay, I won't cancel the order. Let me know if you need anything else!"
            response_data['type'] = 'general'
        
        response_data['context'].pop('awaiting_cancel_confirmation', None)
        response_data['context'].pop('pending_order_number', None)
        return jsonify(response_data)
    
    # ========== NEW QUERY - INTENT DETECTION ==========
    intent = detect_intent(user_message, conversation_context)
    
    # Handle: Track Order
    if intent == 'track_order':
        if order_num:
            order = query_order(order_num)
            if order:
                response_data['message'] = format_order_status_message(order)
                response_data['type'] = 'database_response'
                response_data['order_info'] = order
            else:
                response_data['message'] = f"I couldn't find order #{order_num} in our system. Please double-check the order number or contact support at support@ecommerce.com"
                response_data['type'] = 'error'
        else:
            response_data['message'] = "I can help track your order! Please provide your 5-digit order number."
            response_data['type'] = 'clarification'
            response_data['context']['awaiting_order_number'] = True
    
    # Handle: Return with Order Number
    elif intent == 'return_item_with_order':
        if order_num:
            order = query_order(order_num)
            if order:
                if order['status'] == 'delivered':
                    response_data['message'] = f"I found your order #{order_num} ({order['items']}). You can return it within 30 days. Visit our Returns page: https://ecommerce.com/returns. Need help?"
                    response_data['type'] = 'database_response'
                    response_data['order_info'] = order
                elif order['status'] == 'shipped':
                    response_data['message'] = f"Your order #{order_num} ({order['items']}) is in transit. Once delivered, you can return it within 30 days. Visit: https://ecommerce.com/returns"
                    response_data['type'] = 'database_response'
                elif order['status'] == 'cancelled':
                    response_data['message'] = f"Order #{order_num} has already been cancelled. No return needed."
                    response_data['type'] = 'database_response'
                else:
                    response_data['message'] = f"Order #{order_num} ({order['items']}) is still processing. You can cancel it instead. Would you like to cancel?"
                    response_data['type'] = 'database_response'
                    response_data['context']['awaiting_cancel_confirmation'] = True
                    response_data['context']['pending_order_number'] = order_num
            else:
                response_data['message'] = f"I couldn't find order #{order_num}. Please verify the order number."
                response_data['type'] = 'error'
        else:
            response_data['message'] = "I can help you with a return! Please provide your order number."
            response_data['type'] = 'clarification'
            response_data['context']['awaiting_return_order_number'] = True
    
    # Handle: Return without Order Number
    elif intent == 'return_item':
        response_data['message'] = "I can help with your return! Please provide your 5-digit order number."
        response_data['type'] = 'clarification'
        response_data['context']['awaiting_return_order_number'] = True
    
    # Handle: Change Address
    elif intent == 'change_address' or intent == 'change_address_with_number':
        if order_num:
            order = query_order(order_num)
            if order:
                if order['status'] == 'processing':
                    response_data['message'] = f"I found order #{order_num} ({order['items']}). I'll forward your address change request to our support team. Would you like me to create a ticket?"
                    response_data['type'] = 'escalation'
                    response_data['needs_escalation'] = True
                    response_data['context']['awaiting_address_change_confirmation'] = True
                    response_data['context']['pending_order_number'] = order_num
                elif order['status'] == 'shipped':
                    response_data['message'] = f"Order #{order_num} ({order['items']}) has already shipped. The address cannot be changed. Contact the carrier or wait for delivery."
                    response_data['type'] = 'database_response'
                else:
                    response_data['message'] = f"Order #{order_num} status is '{order['status']}'. Address changes may not be possible."
                    response_data['type'] = 'database_response'
            else:
                response_data['message'] = f"I couldn't find order #{order_num}. Please verify the order number."
                response_data['type'] = 'error'
        else:
            response_data['message'] = "I can help update the delivery address! Please provide your order number."
            response_data['type'] = 'clarification'
            response_data['context']['awaiting_order_for_address'] = True
    
    # Handle: Shipping Info
    elif intent == 'shipping_info':
        kb_info = retrieve_from_knowledge_base('shipping')
        response_data['message'] = kb_info[0] if kb_info else KNOWLEDGE_BASE['shipping_options']
        response_data['type'] = 'knowledge_base_response'
    
    # Handle: Payment Info
    elif intent == 'payment_info':
        kb_info = retrieve_from_knowledge_base('payment')
        response_data['message'] = kb_info[0] if kb_info else KNOWLEDGE_BASE['payment_methods']
        response_data['type'] = 'knowledge_base_response'
    
    # Handle: Cancel Order
    elif intent == 'cancel_order' or intent == 'cancel_order_with_number':
        if order_num:
            order = query_order(order_num)
            if order:
                if order['status'] == 'processing':
                    user_id = order['user_id']
                    issue_desc = f"Cancel order request: Order #{order_num} - {order['items']}"
                    ticket_id = create_ticket(user_id, issue_desc)
                    
                    if ticket_id:
                        response_data['message'] = f"I've created a cancellation request for order #{order_num} ({order['items']}). Our team will process it within 24 hours. Ticket #{ticket_id}."
                        response_data['type'] = 'escalation_confirmed'
                        response_data['ticket_id'] = ticket_id
                    else:
                        response_data['message'] = "I'm sorry, I couldn't create the request. Please contact support@ecommerce.com"
                        response_data['type'] = 'error'
                elif order['status'] == 'shipped':
                    response_data['message'] = f"Order #{order_num} ({order['items']}) has already shipped. You'll need to refuse delivery or return it after receiving."
                    response_data['type'] = 'database_response'
                elif order['status'] == 'cancelled':
                    response_data['message'] = f"Order #{order_num} is already cancelled."
                    response_data['type'] = 'database_response'
                else:
                    response_data['message'] = f"Order #{order_num} status is '{order['status']}'. Please contact support for assistance."
                    response_data['type'] = 'database_response'
            else:
                response_data['message'] = f"I couldn't find order #{order_num}. Please verify the order number."
                response_data['type'] = 'error'
        else:
            response_data['message'] = "I can help cancel your order. Please provide your order number."
            response_data['type'] = 'clarification'
            response_data['context']['awaiting_order_for_cancel'] = True
    
    # Handle: Contact Support
    elif intent == 'contact_support':
        response_data['message'] = KNOWLEDGE_BASE['customer_support']
        response_data['type'] = 'knowledge_base_response'
    
    # Handle: General
    else:
        kb_info = retrieve_from_knowledge_base(user_message)
        if kb_info:
            response_data['message'] = ' '.join(kb_info)
            response_data['type'] = 'knowledge_base_response'
        else:
            gemini_response = generate_gemini_response(user_message, conversation_context)
            response_data['message'] = gemini_response
            response_data['type'] = 'generated_response'
    
    return jsonify(response_data)

@app.route('/api/create_ticket', methods=['POST'])
def create_support_ticket():
    """Create a support ticket"""
    data = request.json
    user_id = data.get('user_id', 1)
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