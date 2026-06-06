@echo off
cd /d "%~dp0"
echo === Step 1: Prepare combined training + validation split ===
python prepare_data.py
echo.
echo === Step 2: Compare algorithms (demo validation 35 comments) ===
python compare_algorithms.py
echo.
echo === Step 3: Evaluate TF-IDF and BERT ===
python evaluate.py --data data/real/validation_manual.csv --model both
python evaluate.py --data data/real/validation_comments.csv --model both
echo.
echo === Step 4: Model comparison summary ===
python compare_models.py --quick
echo.
echo === Step 5: Fine-tune BERT (balanced + class weights, ~30-90 min CPU) ===
python finetune_bert.py --epochs 1 --max-samples 1200 --batch-size 4
echo.
echo === Step 6: Re-evaluate after fine-tune ===
python evaluate.py --data data/real/validation_manual.csv --model bert
python evaluate.py --data data/real/validation_comments.csv --model bert
pause
