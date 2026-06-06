@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo   Demo - Multilingual Sentiment Analysis
echo ========================================
echo.

echo [1/4] Single comment (Arabic Shami)...
python analyze.py --text "الخدمة كتير منيح والتوصيل كان سريع"
echo.

echo [2/4] Batch analysis (sample CSV)...
python analyze.py --file data/sample_comments.csv --output data/demo_results.csv
echo.

echo [3/4] Validation evaluation (TF-IDF)...
python evaluate.py --data data/real/validation_comments.csv
echo.

echo [4/4] Starting UI...
echo Open browser: http://localhost:8501
python -m streamlit run app/main.py
