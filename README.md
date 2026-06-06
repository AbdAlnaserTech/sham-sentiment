# Multilingual Sentiment Analysis — تحليل مشاعr التعليقات

**المطور:** عبد الناصر حسون · **جامعة الشام**

## التشغيل السريع

```powershell
cd sentiment_project
pip install -r requirements.txt
pip install -r requirements_fetch.txt
.\run.bat
```

→ http://localhost:8501

### رفع مجاني على الإنترنت (Streamlit Cloud)

```powershell
# بعد رفع المشروع على GitHub — راجع الدليل الكامل:
# docs/DEPLOY_STREAMLIT_AR.md
```

→ `https://YOUR-APP.streamlit.app`

---

## هيكل المشروع

```
sentiment_project/
├── app/                 # الواجهة (Streamlit)
│   ├── main.py
│   ├── shared.py
│   └── components/
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

---

## أوامر مهمة

| الأمر | الوظيفة |
|-------|---------|
| `.\run.bat` | تشغيل الواجهة |
| `.\improve_accuracy.bat` | تحضير بيانات + fine-tune + تقييم |
| `python fetch_comments.py URL --analyze` | جلب تعليقات حقيقية |
| `python evaluate.py --data data/real/validation_manual.csv --model bert` | تقييم Demo |
| `pytest tests/ -q` | اختبارات |

---

## Docker

```bash
docker compose up --build
```
