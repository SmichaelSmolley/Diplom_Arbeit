@echo off
echo ==============================================
echo Installing Python virtual environment and dependencies
echo ==============================================

python -m venv .venv

echo Activating virtual environment...
call .venv\Scripts\activate

echo Upgrading pip...
pip install --upgrade pip

echo Installing requirements...
pip install -r requirements.txt

echo ==============================================
echo Setup complete!
echo To activate the virtual environment later, run:
echo     call .venv\Scripts\activate
echo ==============================================

pause
