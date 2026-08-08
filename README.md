# Multilingual Sentiment Analysis — تحليل مشاعر التعليقات

**المطور:** عبد الناصر حسون · **جامعة الشام**

## التشغيل السريع

```powershell
cd sentiment_project
pip install -r requirements.txt
.\run.bat
```

→ http://localhost:8501

### رفع على الإنترنت (Streamlit Cloud)

ارفع المستودع على GitHub ثم اربطه من [share.streamlit.io](https://share.streamlit.io).

---

## هيكل المشروع

```
sentiment_project/
├── app/                 # الواجهة (Streamlit)
│   ├── main.py
│   ├── shared.py
│   └── components/
├── launchers/           # wrappers وملفات التشغيل القديمة
├── commands/            # سكربتات العمل اليدوي والنشر
├── src/                 # المنطق الأساسي
│   ├── models/          # TF-IDF + BERT
│   ├── api/             # FastAPI
│   ├── data/            # بيانات + جلب تعليقات
│   └── evaluation/      # LIME + metrics
├── scripts/             # أدوات CLI
├── data/                # datasets
├── models/              # نماذj محفوظة + reports/
├── configs/default.yaml # إعدادات + شعار الجامعة
├── assets/logo.png      # شعار جامعة الشام
├── docs/                # تقرير + دليل العرض
└── tests/               # اختبارات
```

## ملفات الجذر السريعة

هذه الملفات موجودة في الجذر فقط لتسهيل التشغيل من الطرفية، ومعظمها يمرر التنفيذ إلى `scripts/`:

| النوع | الملفات |
|------|---------|
| تشغيل الواجهة | `app.py`, `streamlit_app.py` |
| ملفات التشغيل الخارجية | `launchers/run_api.py`, `launchers/fetch_comments.py`, `launchers/train.py`, `launchers/evaluate.py`, `launchers/analyze.py` |
| تجهيز البيانات والنماذج | `launchers/prepare_data.py`, `launchers/generate_dataset.py`, `launchers/expand_validation.py`, `launchers/download_models.py`, `launchers/download_astd.py`, `launchers/finetune_bert.py` |
| المقارنة والتحسين | `launchers/compare_models.py`, `launchers/compare_algorithms.py`, `commands/improve_accuracy.bat` |
| أدوات مساعدة | `launchers/init_db.py`, `launchers/augmentation.py`, `launchers/inference.py`, `launchers/preprocessing.py`, `launchers/utils.py`, `launchers/_launch.py` |

## التنظيم الصحيح للملفات

- إذا كان الملف ينفّذ من سطر الأوامر أو كان wrapper قديم، فمكانه داخل [launchers/](launchers) أو [scripts/](scripts).
- إذا كان الملف يعرض واجهة للمستخدم، فمكانه داخل [app/](app).
- إذا كان الملف يضم المنطق الأساسي أو طبقة البيانات أو النماذج، فمكانه داخل [src/](src).

---

## أوامر مهمة

| الأمر | الوظيفة |
|-------|---------|
| `.\run.bat` | تشغيل الواجهة |
| `commands/improve_accuracy.bat` | تحضير بيانات + fine-tune + تقييم |
| `python launchers/fetch_comments.py URL --analyze` | جلب تعليقات حقيقية |
| `python launchers/evaluate.py --data data/real/validation_manual.csv --model bert` | تقييم Demo |
| `pytest tests/ -q` | اختبارات |


## Docker

```bash
docker compose up --build
```
