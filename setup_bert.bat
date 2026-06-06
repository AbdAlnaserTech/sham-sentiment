@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Installing BERT dependencies...
pip install -r requirements_bert.txt -q
echo.
echo Downloading models (may take 10-20 minutes)...
python download_models.py
echo.
echo Running quick comparison...
python compare_models.py --quick
echo.
echo Regenerating PDF report...
python docs/generate_pdf.py
echo.
echo Done!
pause
