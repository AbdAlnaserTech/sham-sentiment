# خريطة دراسة المشروع — بعد الترتيب

> **قاعدة:** ادرس من `app/main.py` → `app/tabs/` → `src/`  
> كل ما خارج هذا المسار **ليس في الواجهة** وتم حذفه.

---

## 1. هيكل الواجهة (ابدأ هنا)

```
app/
├── main.py              ← نقطة الدخول (80 سطر — توجيه فقط)
├── shared.py            ← تهيئة + BERT + الشريط الجانبي
├── bootstrap.py         ← ربط app/ مع src/
│
├── tabs/                ← ★ كل تبويب = ملف ★
│   ├── dashboard.py     ← تبويب 1: لوحة التحكم
│   ├── single.py        ← تبويب 2: تعليق واحد
│   ├── batch.py         ← تبويب 3: مجموعة تعليقات
│   ├── live.py          ← تبويب 4: جلب من الإنترنت
│   ├── about.py         ← تبويب 5: حول المشروع
│   └── batch_helpers.py ← مشترك بين batch و live
│
└── components/          ← عناصر UI مشتركة (ليست تبويبات)
    ├── auth_panel.py    ← تسجيل الدخول + صلاحيات
    ├── app_header.py    ← رأس + تذييل + شعار
    ├── sidebar_panel.py ← الشريط الجانبي
    ├── ui_styles.py     ← CSS
    ├── batch_results.py ← جدول وتحليل الدفعات
    ├── analytics_panel.py ← حفظ + PDF/Excel
    ├── sentiment_display.py ← بطاقة النتيجة
    ├── charts.py        ← Pie chart
    ├── wordcloud.py     ← سحابة كلمات
    └── demo_samples.py  ← أمثلة جاهزة
```

---

## 2. ترتيب الدراسة (يوم بيوم)

| اليوم | اقرأ | ماذا تفهم |
|-------|------|-----------|
| 1 | `main.py` | التدفق: login → tabs |
| 2 | `tabs/single.py` + `components/sentiment_display.py` | تحليل تعليق واحد |
| 3 | `shared.py` → `src/models/registry.py` → `bert_predictor.py` | BERT |
| 4 | `src/language.py` | كشف اللغة |
| 5 | `tabs/batch.py` + `batch_helpers.py` + `batch_results.py` | تحليل جماعي |
| 6 | `tabs/live.py` + `src/data/comment_fetcher.py` | جلب YouTube/Play |
| 7 | `tabs/dashboard.py` + `src/db/` | SQLite + لوحة |
| 8 | `tabs/about.py` | عرض المشروع |

---

## 3. المنطق الأساسي (src/)

```
src/
├── language.py          ← كشف اللغة (قواعد)
├── config.py            ← إعدادات YAML
├── paths.py             ← مسارات المجلدات
├── cloud_setup.py       ← Streamlit Cloud
├── logging_utils.py
│
├── models/
│   ├── registry.py      ← load_predictor() → BERT
│   └── bert_predictor.py ← النموذج الوحيد
│
├── db/
│   ├── database.py      ← SQLite
│   ├── auth.py          ← كلمات المرور
│   ├── repository.py    ← حفظ/قراءة
│   └── batch_ops.py     ← حذف دفعات
│
├── data/
│   └── comment_fetcher.py ← جلب التعليقات
│
├── analytics/
│   └── alerts.py        ← تنبيهات سلبية
│
└── reports/
    └── export.py        ← PDF / Excel
```

---

## 4. تدفق تحليل تعليق واحد

```
main.py → tabs/single.py
    → shared.get_predictor()
    → registry.load_predictor()
    → bert_predictor.predict_with_confidence()
    → sentiment_display.py (عرض)
```

---

## 5. ما تم حذفه (ليس في الواجهة)

| محذوف | السبب |
|-------|--------|
| `scripts/` + `launchers/` | أوامر CLI — ليست UI |
| `commands/*.bat` | ما عدا run.bat |
| `src/api/` | FastAPI — ليست Streamlit |
| `src/evaluation/` | تقييم تدريب — ليس UI |
| `src/preprocessing.py` | كان لـ TF-IDF |
| `src/analytics/keywords.py` | غير مستخدم بالواجهة |
| `src/data/*` (ما عدا comment_fetcher) | توليد/دمج datasets |
| `app.py`, `streamlit_app.py` | نقاط دخول مكررة |

---

## 6. التشغيل

```powershell
cd sentiment_project
.\run.bat
```

---

*مشروع تخرج 2026 — جامعة الشام*
