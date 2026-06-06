# Presentation Guide — دليل العرض

## مدة العرض: 15 دقيقة

| # | الشريحة | الوقت |
|---|---------|-------|
| 1 | العنوان + المقدمة | 1m |
| 2 | المشكلة والأهداف | 1.5m |
| 3 | Methodology (مخطط) | 2m |
| 4 | Demo: تعليق واحد | 2m |
| 5 | Demo: مجموعة تعليقات | 2m |
| 6 | LIME Explanation | 1.5m |
| 7 | Validation Results | 2m |
| 8 | API + Architecture | 1.5m |
| 9 | Future Work + Conclusion | 1.5m |

## Demo Script

### 1. تعليق واحد (شامي)
```
الخدمة كتير منيح والتوصيل كان سريع
```
→ إيجابي + ثقة + LIME

### 2. مجموعة تعليقات
ارفع `data/sample_comments.csv` → اعرض الملخص

### 3. API (اختياري)
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"الخدمة كتير منيح\", \"explain\": true}"
```

## نقاط القوة للتركيز
- 3 لغات/أنماط
- تعليق واحد + مجموعة
- LIME explainability
- Validation واقعي
- API + UI + CLI

## أسئلة متوقعة

**س: لماذا 100% على التدريب؟**
> البيانات الاصطناعية. قيّمنا على validation_comments.csv للنتائج الواقعية.

**س: لماذا TF-IDF وليس BERT؟**
> سرعة + بساطة + مناسب للتعليقات القصيرة. BERT في future work.

**س: كيف تفرق فصحى/شامي؟**
> قاموس كلمات دلالية + preprocessing مخصص.

**س: Limitations?**
> Sarcasm, aspect-based, dialects أخرى — future work.
