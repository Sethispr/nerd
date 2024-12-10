@echo off

REM Define the working directory
set BOT_DIR=%USERPROFILE%\Documents\bot

REM Navigate to the bot directory, make one or modify the directory above
if not exist "%BOT_DIR%" (
    echo ERROR: Bot directory does not exist: %BOT_DIR%
    pause
)
cd "%BOT_DIR%"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    pause
)

echo [INFO] Installing dependencies from requirements.txt..

REM Install dependencies from requirements.txt
if not exist "requirements.txt" (
    echo ERROR: requirements.txt file not found.
    pause
)

pip install -r requirements.txt
echo [INFO] Dependencies successfully/already installed!

if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
)

REM Run the Python script
if not exist "main.py" (
    echo ERROR: main.py file not found.
    pause
)

python main.py
if errorlevel 1 (
    echo ERROR: An error occurred while running the bot.
    pause
)

REM Pause at the end to review output
pause
