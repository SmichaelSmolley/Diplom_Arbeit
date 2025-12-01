@echo off
echo =Installing Python virtual environment and dependencies=
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
echo =Setup complete. To activate the virtual environment, run: .venv\Scripts\activate=