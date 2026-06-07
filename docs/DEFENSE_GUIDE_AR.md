# دليل الدفاع — مشروع تحليل المشاعر

**الطالب:** عبد الناصر حسون · **جامعة الشام**

## الروابط

| | |
|---|---|
| GitHub | https://github.com/AbdAlnaserTech/sham-sentiment |
| التطبيق | https://sham-sentiment.streamlit.app |
| محلي | `.\run.bat` → http://localhost:8501 |

## حسابات العرض

| الدور | مستخدم | كلمة مرور |
|-------|--------|-----------|
| مدير | admin | Admin@2026 |
| محلل | analyst | Analyst@2026 |
| عرض | viewer | Viewer@2026 |

## سينario العرض (10–12 دقيقة)

### 1. المقدمة (1 د)
- مشكلة: تحليل آراء العملاء بالعربية والإنجليزية
- الحل: منصة متكاملة (UI + API + DB + AI)

### 2. Demo — تعليق واحد (2 د)
- النموذج: **BERT**
- النص: `الخدمة كتير منيح والتوصيل كان سريع`
- اعرض: مشاعر + ثقة + رسم + LIME

### 3. Demo — مجموعة (2 د)
- زر «تحميل أمثلة الدفعة» من الشريط الجانبي
- حلّل → ملخص → كلمات مفتاحية → تنبيه → **تصدير PDF**

### 4. لوحة التحكم (1 د)
- KPIs + توزيع + سجل الدفعات

### 5. التقنية (2 د)
- TF-IDF (سريع + LIME) vs BERT (أدق)
- F1 ≈ **76%** demo · ≈ **63%** full validation
- SQLite + صلاحيات + Streamlit Cloud

### 6. الخاتمة (1 د)
- GitHub + رابط مباشر + QR

## أسئلة متوقعة

**لماذا BERT وليس TF-IDF فقط؟**  
BERT يفهم السياق؛ TF-IDF أسرع ويُستخدم مع LIME للشرح.

**كيف تقيس الدقة؟**  
Validation على `validation_comments.csv` — Macro F1 و Accuracy.

**SQLite أم PostgreSQL؟**  
SQLite للتخرج؛ PostgreSQL للإنتاج (موثّق في ARCHITECTURE.md).

**هل يدعم Facebook؟**  
لا — قيود API. YouTube / Play / Reddit + CSV.

**الفرق عن مشاريع أخرى؟**  
منصة كاملة: auth، dashboard، API، جلب حي، تصدير، سحابة.

## قبل يوم الدفاع

- [ ] افتح السحابة قبل العرض بـ 10 دقائق (تحميل BERT)
- [ ] جرّب admin + viewer
- [ ] احذف GitHub Token القديم
- [ ] PowerPoint + QR من تبويب «حول المشروع»
