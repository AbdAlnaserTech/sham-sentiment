# تقرير مشروع التخرج

## تحليل المشاعر متعدد اللغات
**English + Arabic Fusha + Arabic Shami**

---

## 1. المقدمة

### 1.1 خلفية المشروع
تحليل المشاعر (Sentiment Analysis) هو أحد تطبيقات معالجة اللغة الطبيعية (NLP) الأكثر استخداماً في تحليل آراء العملاء، مراقبة وسائل التواصل، ودعm قرارات الأعمال.

### 1.2 مشكلة البحث
معظم أنظمة تحليل المشاعر تركز على الإنجليزية، بينما اللغة العربية — خاصة الفصحى واللهجات — تفتقر لحلول عملية متكاملة في مشاريع التخرج.

### 1.3 أهداف المشروع
1. بناء نظام يصنّف التعليقات إلى: **إيجابي / سلبي / محايد**
2. دعم **3 أنماط لغوية**: English, Arabic Fusha, Arabic Shami
3. توفير **ثقة معايرة** (Calibrated Confidence) لكل تنبؤ
4. تمكين التحليل **لتعليق واحد أو مجموعة تعليقات**
5. شرح قرارات النموذج عبر **LIME**

---

## 2. الأعمال ذات الصلة

| المرجع | الوصف |
|--------|-------|
| TF-IDF + Logistic Regression | Baseline كلاسيكي سريع للنصوص القصيرة |
| CalibratedClassifierCV | معايرة احماليات التنبؤ |
| LIME | شرح قرارات النماذج على مستوى الكلمات |
| ASTD / ArSentD-LEV | Datasets عربية للمشاعر (للتوسع المستقبلي) |

---

## 3. منهجية العمل

```
Input Text
    ↓
Language Detection (en / ar_fusha / ar_shami)
    ↓
Preprocessing (normalization, stopwords, emoji tokens)
    ↓
TF-IDF Vectorization (1-2 grams, 15000 features)
    ↓
Logistic Regression / Linear SVM (GridSearchCV)
    ↓
Sigmoid Calibration
    ↓
Sentiment + Confidence + Explanation (LIME)
```

---

## 4. البيانات

### 4.1 بيانات التدريب (Synthetic)
- ~5000 جملة مُولَّدة من قوالب متنوعة
- توزيع متوازن على 3 لغات × 3 مشاعر
- Augmentation: إيموجي، هاشتاغ، مرادفات

### 4.2 بيانات التحقق (Real-style)
- `data/real/validation_comments.csv` — 35 تعليقاً حقيقياً الشكل
- تُستخدم للتقييم الصادق خارج بيانات التدريب الاصطناعية

> **ملاحظة أكاديمية:** الدقة 100% على البيانات الاصطناعية متوقعة لأن الأنماط واضحة. التقييم على `validation_comments.csv` يعكس أداءً أكثر واقعية.

---

## 5. النموذج والتقييم

### 5.1 النموذج المختار
- **TF-IDF + Logistic Regression** (أفضل F1 في Cross-Validation)
- **Calibration:** Sigmoid, 5-fold

### 5.2 المقاييس
- Precision, Recall, F1 (macro)
- Confusion Matrix
- ROC Curve (one-vs-rest)
- Calibration Plot

### 5.3 مقارنة TF-IDF vs BERT (Validation)

| النموذج | Macro F1 | Accuracy |
|---------|----------|----------|
| TF-IDF + LogReg | 0.619 | 0.629 |
| XLM-RoBERTa (BERT) | **0.759** | **0.800** |

> BERT أفضل على التعليقات الحقيقية بـ +14 نقطة F1

### 5.4 التشغيل
```bash
python train.py --data data/sentiment_dataset_multilingual.csv
python evaluate.py --data data/real/validation_comments.csv
```

---

## 6. النظام المطوّر

### 6.1 الواجهة (Streamlit)
- تبويب تعليق واحد + LIME + Word Cloud
- تبويب مجموعة تعليقات (لصق أو CSV)

### 6.2 API (FastAPI)
```
POST /api/v1/analyze       — تعليق واحد
POST /api/v1/batch         — مجموعة تعليقات
POST /api/v1/batch/upload  — رفع CSV
GET  /api/v1/health        — فحص الحالة
```

### 6.3 CLI
```bash
python analyze.py --text "..."
python analyze.py --file data/sample_comments.csv
```

---

## 7. الابتكار

1. **Dialect-Aware Pipeline** — تمييز فصحى/شامي
2. **Confidence-Aware System** — تحذير عند ثقة < 55%
3. **LIME Explainability** — ليس black box
4. **Batch + API + UI** — جاهز للاستخدام العملي

---

## 8. النتائج

راجع:
- `models/model_metadata.json`
- `models/validation_report.json`
- `models/plots/`

---

## 9. التحديات والحلول

| التحدي | الحل |
|--------|------|
| قلة البيانات العربية | Synthetic + validation set |
| دقة 100% مشبوهة | تقييم منفصل على validation |
| sarcasm | Future work — BERT |
| سرعة vs دقة | TF-IDF للسرعة، BERT اختياري |

---

## 10. Future Work

- [ ] دمج ASTD / ArSentD-LEV
- [ ] Fine-tune CAMeLBERT
- [ ] Aspect-Based Sentiment Analysis
- [ ] Real-time social media monitor
- [ ] Mobile app

---

## 11. الخلاصة

تم بناء نظام متكامل لتحليل مشاعر التعليقات بعدة لغات، مع واجهة وAPI وCLI، وشرح قرارات النموذج، وتقييم واقعي على مجموعة تحقق مستقلة.

---

## المراجع
1. scikit-learn Documentation — Text Classification
2. Ribeiro et al. — "Why Should I Trust You?" (LIME)
3. Arabic Sentiment Analysis Literature (ASTD, ArSentD)
