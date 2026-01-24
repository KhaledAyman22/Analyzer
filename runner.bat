@echo off
cd /d %~dp0

:: Activate virtual environment
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate

:: Install requirements
echo Installing requirements...
pip install --upgrade pip
pip install -r requirements.txt

:: Run Streamlit
echo Starting Streamlit...
python -m streamlit run app.py

pause