@echo off
chcp 65001 > nul
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo [1/3] Dang tao moi truong ao...
    python -m venv venv
)

call "venv\Scripts\activate.bat"

echo [2/3] Dang cai dat thu vien...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo [3/3] Dang khoi dong ung dung...
streamlit run app.py
pause
