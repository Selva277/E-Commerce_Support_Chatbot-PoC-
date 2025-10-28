@echo off
REM Windows Setup Checker for E-commerce Support Chatbot
REM Save this as check_setup.bat

echo ========================================================================
echo           E-commerce Support Chatbot - Setup Checker (Windows)
echo ========================================================================
echo.

REM Check Python Installation
echo [1/8] Checking Python Installation...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python is installed
    python --version
) else (
    echo [ERROR] Python is NOT installed
    echo Please install Python 3.8 or higher from https://www.python.org/
    goto :end
)
echo.

REM Check pip
echo [2/8] Checking pip...
pip --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] pip is available
) else (
    echo [ERROR] pip is NOT available
    goto :end
)
echo.

REM Check if requirements.txt exists
echo [3/8] Checking requirements.txt...
if exist requirements.txt (
    echo [OK] requirements.txt found
) else (
    echo [ERROR] requirements.txt NOT found
    goto :end
)
echo.

REM Check Python packages
echo [4/8] Checking Python packages...
pip show Flask >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Flask is installed
) else (
    echo [WARNING] Flask is NOT installed
    echo Run: pip install -r requirements.txt
)

pip show flask-cors >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Flask-CORS is installed
) else (
    echo [WARNING] Flask-CORS is NOT installed
)

pip show mysql-connector-python >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] mysql-connector-python is installed
) else (
    echo [WARNING] mysql-connector-python is NOT installed
)

pip show google-generativeai >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] google-generativeai is installed
) else (
    echo [WARNING] google-generativeai is NOT installed
)
echo.

REM Check MySQL
echo [5/8] Checking MySQL...
mysql --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] MySQL client is installed
    mysql --version
) else (
    echo [WARNING] MySQL client not found in PATH
    echo Make sure MySQL is installed and running
)
echo.

REM Check project files
echo [6/8] Checking project files...
if exist app.py (
    echo [OK] app.py found
) else (
    echo [ERROR] app.py NOT found
)

if exist database_setup.sql (
    echo [OK] database_setup.sql found
) else (
    echo [ERROR] database_setup.sql NOT found
)

if exist templates\index.html (
    echo [OK] templates\index.html found
) else (
    echo [ERROR] templates\index.html NOT found
    echo Make sure index.html is in the templates folder
)
echo.

REM Check API key configuration
echo [7/8] Checking Gemini API key...
findstr /C:"YOUR_GEMINI_API_KEY" app.py >nul 2>&1
if %errorlevel% equ 0 (
    echo [WARNING] Gemini API key is NOT configured
    echo Replace YOUR_GEMINI_API_KEY in app.py with your actual key
) else (
    echo [OK] Gemini API key appears to be configured
)
echo.

REM Check port 5000
echo [8/8] Checking port 5000...
netstat -an | findstr ":5000" >nul 2>&1
if %errorlevel% equ 0 (
    echo [WARNING] Port 5000 is already in use
    echo Stop any running Flask applications
) else (
    echo [OK] Port 5000 is available
)
echo.

REM Summary
echo ========================================================================
echo                              SUMMARY
echo ========================================================================
echo.
echo If all checks passed, you can start the application with:
echo     python app.py
echo.
echo Then open your browser to: http://localhost:5000
echo.
echo Common setup steps if checks failed:
echo 1. Install dependencies: pip install -r requirements.txt
echo 2. Setup MySQL database: mysql -u root -p ^< database_setup.sql
echo 3. Configure Gemini API key in app.py
echo 4. Ensure MySQL server is running
echo 5. Create templates folder and move index.html there
echo.
echo For detailed checking, run: python check_setup.py
echo ========================================================================

:end
echo.
pause