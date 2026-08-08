@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo   Multilingual Sentiment Analysis
echo   جامعة الشام - مشروع التخرج
echo ========================================
echo.
echo Starting Streamlit on http://localhost:8501
echo Press Ctrl+C to stop.
echo.
python -m streamlit run app\main.py