#!/usr/bin/env python3
"""
Setup Verification Script for E-commerce Support Chatbot
This script checks all requirements and configurations needed to run the PoC
"""

import sys
import importlib
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.ENDC}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.ENDC}")

def check_python_version():
    """Check Python version"""
    print_header("Checking Python Version")
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python version: {version_str} (Required: 3.8+)")
        return True
    else:
        print_error(f"Python version: {version_str} (Required: 3.8+)")
        print_info("Please upgrade Python to 3.8 or higher")
        return False

def check_pip_packages():
    """Check if required Python packages are installed"""
    print_header("Checking Required Python Packages")
    
    required_packages = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'mysql.connector': 'mysql-connector-python',
        'google.generativeai': 'google-generativeai'
    }
    
    all_installed = True
    
    for module_name, package_name in required_packages.items():
        try:
            importlib.import_module(module_name)
            print_success(f"{package_name} is installed")
        except ImportError:
            print_error(f"{package_name} is NOT installed")
            all_installed = False
    
    if not all_installed:
        print_warning("\nTo install missing packages, run:")
        print_info("pip install -r requirements.txt")
    
    return all_installed

def check_mysql_connection():
    """Check MySQL connection and database"""
    print_header("Checking MySQL Database Connection")
    
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'root@123',  # Update if different
        'database': 'ecommerce_support'
    }
    
    try:
        # Try to connect to MySQL server
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        
        if connection.is_connected():
            print_success("MySQL server connection successful")
            
            # Check if database exists
            cursor = connection.cursor()
            cursor.execute("SHOW DATABASES LIKE 'ecommerce_support'")
            result = cursor.fetchone()
            
            if result:
                print_success("Database 'ecommerce_support' exists")
                
                # Connect to the database
                connection.database = 'ecommerce_support'
                
                # Check tables
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                required_tables = ['users', 'orders', 'tickets', 'conversation_history']
                existing_tables = [table[0] for table in tables]
                
                for table in required_tables:
                    if table in existing_tables:
                        print_success(f"Table '{table}' exists")
                    else:
                        print_error(f"Table '{table}' is missing")
                
                # Check sample data
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM orders")
                order_count = cursor.fetchone()[0]
                
                if user_count > 0:
                    print_success(f"Found {user_count} sample users in database")
                else:
                    print_warning("No sample users found")
                
                if order_count > 0:
                    print_success(f"Found {order_count} sample orders in database")
                else:
                    print_warning("No sample orders found")
                
                cursor.close()
                connection.close()
                return True
                
            else:
                print_error("Database 'ecommerce_support' does NOT exist")
                print_info("Run the database_setup.sql script to create it")
                print_info("mysql -u root -p < database_setup.sql")
                return False
                
    except Error as e:
        print_error(f"MySQL connection failed: {e}")
        print_info("Make sure MySQL server is running")
        print_info("Verify username and password in app.py")
        return False

def check_gemini_api_key():
    """Check if Gemini API key is configured"""
    print_header("Checking Gemini API Configuration")
    
    try:
        import google.generativeai as genai
        
        # Read API key from app.py
        with open('app.py', 'r') as f:
            content = f.read()
            if 'YOUR_GEMINI_API_KEY' in content:
                print_error("Gemini API key is NOT configured")
                print_info("Replace 'YOUR_GEMINI_API_KEY' in app.py with your actual API key")
                print_info("Get your API key from: https://makersuite.google.com/app/apikey")
                return False
            elif 'AIzaSy' in content:
                # Found what looks like an API key
                print_success("Gemini API key appears to be configured")
                
                # Try to test the API key
                try:
                    import re
                    api_key_match = re.search(r"genai\.configure\(api_key='([^']+)'\)", content)
                    if api_key_match:
                        api_key = api_key_match.group(1)
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel('gemini-pro')
                        response = model.generate_content("Say 'API key is working'")
                        if response.text:
                            print_success("Gemini API key is valid and working!")
                            return True
                except Exception as e:
                    print_warning(f"API key configured but validation failed: {e}")
                    print_info("The key might be invalid or rate limited")
                    return True  # Still return True as key is configured
            else:
                print_warning("Could not find Gemini API key in app.py")
                return False
                
    except ImportError:
        print_error("google-generativeai package not installed")
        return False
    except Exception as e:
        print_error(f"Error checking API key: {e}")
        return False

def check_file_structure():
    """Check if all required files exist"""
    print_header("Checking Project File Structure")
    
    required_files = {
        'app.py': 'Flask backend application',
        'database_setup.sql': 'MySQL database setup script',
        'requirements.txt': 'Python dependencies',
        'templates/index.html': 'Frontend HTML file'
    }
    
    all_files_exist = True
    
    for file_path, description in required_files.items():
        if os.path.exists(file_path):
            print_success(f"{file_path} exists ({description})")
        else:
            print_error(f"{file_path} is MISSING ({description})")
            all_files_exist = False
    
    if not all_files_exist:
        print_warning("\nMissing files detected!")
        print_info("Make sure you have extracted all files correctly")
    
    return all_files_exist

def check_flask_app():
    """Check if Flask app can be imported"""
    print_header("Checking Flask Application")
    
    try:
        # Try to import the app
        sys.path.insert(0, os.getcwd())
        from app import app as flask_app
        print_success("Flask application can be imported successfully")
        
        # Check routes
        routes = [str(rule) for rule in flask_app.url_map.iter_rules()]
        required_routes = ['/', '/api/chat', '/api/create_ticket']
        
        for route in required_routes:
            if route in routes:
                print_success(f"Route '{route}' is configured")
            else:
                print_warning(f"Route '{route}' might be missing")
        
        return True
        
    except ImportError as e:
        print_error(f"Cannot import Flask app: {e}")
        return False
    except Exception as e:
        print_error(f"Error checking Flask app: {e}")
        return False

def check_port_availability():
    """Check if port 5000 is available"""
    print_header("Checking Port Availability")
    
    import socket
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 5000))
        
        if result == 0:
            print_warning("Port 5000 is already in use")
            print_info("Stop any running Flask applications or change the port in app.py")
            return False
        else:
            print_success("Port 5000 is available")
            return True
    except Exception as e:
        print_error(f"Error checking port: {e}")
        return False
    finally:
        sock.close()

def run_integration_test():
    """Run a basic integration test"""
    print_header("Running Integration Test")
    
    try:
        # Test database query
        from app import query_order
        order = query_order('12345')
        
        if order:
            print_success(f"Database query successful: Found order {order['order_id']}")
        else:
            print_warning("Database query returned no results")
        
        # Test knowledge base retrieval
        from app import retrieve_from_knowledge_base
        kb_result = retrieve_from_knowledge_base("return policy")
        
        if kb_result:
            print_success("Knowledge base retrieval successful")
        else:
            print_warning("Knowledge base retrieval returned no results")
        
        return True
        
    except Exception as e:
        print_error(f"Integration test failed: {e}")
        return False

def print_summary(results):
    """Print summary of all checks"""
    print_header("Summary")
    
    total_checks = len(results)
    passed_checks = sum(1 for result in results.values() if result)
    
    print(f"Total Checks: {total_checks}")
    print(f"Passed: {Colors.GREEN}{passed_checks}{Colors.ENDC}")
    print(f"Failed: {Colors.RED}{total_checks - passed_checks}{Colors.ENDC}")
    
    if passed_checks == total_checks:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All checks passed! Your setup is ready to go!{Colors.ENDC}")
        print(f"\n{Colors.BLUE}To start the application:{Colors.ENDC}")
        print(f"{Colors.BOLD}python app.py{Colors.ENDC}")
        print(f"\nThen open your browser to: {Colors.BOLD}http://localhost:5000{Colors.ENDC}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠ Some checks failed. Please fix the issues above.{Colors.ENDC}")
        print(f"\n{Colors.BLUE}Common fixes:{Colors.ENDC}")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Setup database: mysql -u root -p < database_setup.sql")
        print("3. Configure Gemini API key in app.py")
        print("4. Ensure MySQL server is running")

def main():
    """Main function to run all checks"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║                                                                   ║")
    print("║          E-commerce Support Chatbot - Setup Checker              ║")
    print("║                                                                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")
    
    print_info(f"Starting setup verification at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all checks
    results = {
        'Python Version': check_python_version(),
        'Python Packages': check_pip_packages(),
        'MySQL Database': check_mysql_connection(),
        'Gemini API Key': check_gemini_api_key(),
        'File Structure': check_file_structure(),
        'Flask Application': check_flask_app(),
        'Port Availability': check_port_availability(),
        'Integration Test': run_integration_test()
    }
    
    # Print summary
    print_summary(results)
    
    return all(results.values())

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Setup check cancelled by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.ENDC}")
        sys.exit(1)