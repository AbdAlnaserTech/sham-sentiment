# Presentation Guide — دليل العرض

## الروابط

- **GitHub:** https://github.com/AbdAlnaserTech/sham-sentiment
- **Live:** https://sham-sentiment.streamlit.app
- **دليل الدفاع:** `docs/DEFENSE_GUIDE_AR.md`

## مدة العرض: 12–15 دقيقة

| # | الشريحة | الوقت |
|---|---------|-------|
| 1 | العنوان + المقدمة | 1m |
| 2 | المشكلة والأهداف | 1.5m |
| 3 | Methodology (مخطط) | 2m |
| 4 | Demo: تعليق واحد (BERT) | 2m |
| 5 | Demo: مجموعة + PDF | 2m |
| 6 | LIME + لوحة التحكم | 2m |
| 7 | Validation + السحابة | 2m |
| 8 | API + الخاتمة | 1.5m |

## Demo Script

### 1. تسجيل دخول
`admin` / `Admin@2026`

### 2. تعليق واحد (شامي)
```
الخدمة كتير منيح والتوصيل كان سريع
```
→ BERT → إيجابي + ثقة + LIME

### 3. مجموعة تعليقات
الشريط الجانبي → **تحميل أمثلة الدفعة** → تحليل → PDF

### 4. حول المشروع
QR + GitHub + حساب viewer

## أسئلة متوقعة

**س: لماذا BERT؟**  
> أفهم السياق — F1 ≈ 76% على عيّنة العرض.

**س: لماذا TF-IDF أيضاً؟**  
> سرعة + LIME لشرح القرار.

**س: الدقة على الاختبار الكامل؟**  
> BERT F1 ≈ 63% على 513 تعليق حقيقي.

**س: Limitations?**  
> Sarcasm، لهجات أخرى، Facebook API — future work.
