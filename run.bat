@echo off
REM ═══════════════════════════════════════════════════════════════════════════
REM تشغيل واجهة Streamlit — مشروع تحليل المشاعر
REM يفتح المتصفح على http://localhost:8501
REM ═══════════════════════════════════════════════════════════════════════════
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
REM نقطة الدخول: app/main.py (الواجهة الرئيسية)
python -m streamlit run app\main.py
