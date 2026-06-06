# رفع المشروع على Streamlit Cloud (مجاني)

## المتطلبات

1. حساب [GitHub](https://github.com) (مجاني)
2. حساب [Streamlit Community Cloud](https://share.streamlit.io) (مجاني)
3. المستودع **Public** (عام) — شرط Streamlit المجاني

## الخطوة 1 — رفع الكود على GitHub

افتح PowerShell داخل مجلد `sentiment_project`:

```powershell
cd "c:\Users\nasser hassoun\OneDrive\المستندات\Desktop\التخرج\sentiment_project"

git init
git add .
git commit -m "Deploy: sentiment analysis platform"
```

أنشئ مستودعاً جديداً على GitHub (مثلاً `sentiment-graduation`) ثم:

```powershell
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/sentiment-graduation.git
git push -u origin main
```

> استبدل `YOUR_USERNAME` واسم المستودع بقيمك.

## الخطوة 2 — ربط Streamlit Cloud

1. ادخل إلى https://share.streamlit.io
2. **New app** → اختر المستودع `sentiment-graduation`
3. Branch: `main`
4. **Main file path:** `streamlit_app.py` (أو `app/main.py`)
5. **App URL:** اختر اسماً مثل `sham-sentiment`
6. **Advanced settings → Secrets** — الصق:

```toml
SENTIMENT_CLOUD = "1"
SENTIMENT_CLOUD_LIGHT = "1"
SENTIMENT_MAX_BATCH = "100"
```

7. اضغط **Deploy**

## الخطوة 3 — أول تشغيل

- أول فتح للتطبيق قد يستغرق **3–8 دقائق** (تحميل PyTorch + نموذج BERT).
- بعدها يظهر تسجيل الدخول:
  - **admin** / **Admin@2026**
  - **analyst** / **Analyst@2026**

## حسابات العرض

| الدور | المستخدم | كلمة المرور |
|-------|----------|-------------|
| مدير | admin | Admin@2026 |
| محلل | analyst | Analyst@2026 |

## ملاحظات مهمة

| الموضوع | التفاصيل |
|---------|----------|
| الذاكرة | الخطة المجانية ~1 GB — يُستخدم نموذj BERT واحد (XLM-RoBERTa) |
| قاعدة البيانات | SQLite مؤقتة — تُعاد عند إعادة النشر |
| TF-IDF | يحتاج `models/sentiment_model.pkl` — شغّل `python train.py` محلياً ثم ارفعه |
| الدفعات | حد 100 تعليق على السحابة (100 على السحابة vs 2000 محلياً) |

## إذا فشل النشر

1. **Logs** في Streamlit Cloud → ابحث عن `MemoryError` أو `OutOfMemory`
2. جرّب في Secrets: `SENTIMENT_CLOUD_LIGHT = "1"`
3. استخدم **TF-IDF** بعد تدريب النموذj محلياً ورفع `sentiment_model.pkl`

## رابطك بعد النشر

```
https://YOUR-APP-NAME.streamlit.app
```

ضع هذا الرابط في تقرير التخرج وعروض PowerPoint.
