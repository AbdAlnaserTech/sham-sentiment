# دليل شرح الأكواد — مشروع تحليل المشاعر

> مرجع للمناقشة: يشرح **كل مجلد وملف** + **تدفق التنفيذ** + **البلوكات الرئيسية**  
> التعليقات داخل الملفات نفسها موجودة في الملفات الأساسية (`app/main.py`, `src/language.py`, …)

---

## 1. هيكل المشروع (شجرة المجلدات)

```
sentiment_project/
├── app/                 ← واجهة Streamlit (ما يراه المستخدم)
├── src/                 ← المنطق الأساسي (نماذج، DB، API، معالجة)
├── scripts/             ← أوامر سطرية (تدريب، تقييم، جلب)
├── launchers/           ← غلافات رفيعة تستدعي scripts/
├── commands/            ← ملفات .bat للتشغيل السريع على Windows
├── configs/             ← إعدادات YAML
├── data/                ← بيانات CSV + قاعدة SQLite
├── models/              ← نماذج محفوظة (.pkl, BERT, تقارير)
├── tests/               ← اختبارات pytest
├── docs/                ← تقرير، عرض، أدلة
├── run.bat              ← تشغيل الواجهة
├── app.py               ← نقطة دخول Streamlit
└── requirements.txt     ← المكتبات
```

---

## 2. مجلد `app/` — الواجهة

| الملف | الدور |
|-------|--------|
| `main.py` | **القلب**: تسجيل دخول → تبويبات → تحليل فردي/جماعي/جلب |
| `shared.py` | تهيئة، cache لـ BERT، الشريط الجانبي، كشف اللغة |
| `bootstrap.py` | يضيف `src/` إلى `sys.path` حتى تعمل الاستيرادات |
| `components/about_panel.py` | تبويب «حول المشروع» — فكرة، فريق، تقنيات |
| `components/auth_panel.py` | نموذج تسجيل الدخول + صلاحيات (admin/analyst/viewer) |
| `components/dashboard_panel.py` | لوحة KPIs، رسوم، تنبيهات، سجل الدفعات |
| `components/batch_results.py` | parsing تعليقات، DataFrame، جدول نتائج |
| `components/live_import.py` | جلب تعليقات YouTube / Google Play |
| `components/sentiment_display.py` | عرض بطاقة النتيجة (إيجابي/سلبي/محايد) |
| `components/analytics_panel.py` | حفظ النتائج في DB + تحليلات إضافية |
| `components/charts.py` | Pie chart لتوزيع المشاعر |
| `components/wordcloud.py` | سحابة كلمات |
| `components/ui_styles.py` | CSS للوضع الداكن و RTL |
| `components/demo_samples.py` | أمثلة جاهزة للتجربة |

### تدفق `main.py` (بلوك ببلوك)

1. **استيراد bootstrap** — يسمح بـ `from language import …` من داخل `app/`
2. **st.set_page_config** — عنوان الصفحة، أيقونة، layout عريض
3. **init_app()** — مجلدات + DB + YAML + session_state
4. **render_login_form** — إن فشل → `st.stop()`
5. **render_sidebar_settings** — لغة، مظهر، RTL
6. **can_analyze()** — viewer يرى لوحة + حول فقط
7. **5 تبويبات** — dashboard | single | batch | live | about
8. **_execute_batch_analysis** — BERT على قائمة → session_state
9. **_render_batch_results_view** — ملخص + جدول + CSV + حفظ

---

## 3. مجلد `src/` — المنطق الأساسي

### 3.1 الجذر

| الملف | الدور |
|-------|--------|
| `language.py` | كشف اللغة (en / ar_fusha / ar_shami) بقواعد + SHAMI_HINT_WORDS |
| `preprocessing.py` | تنظيف نص لمسار TF-IDF (إيموجي، stopwords، تطبيع) |
| `config.py` | قراءة `configs/default.yaml` → كائن AppConfig |
| `paths.py` | مسارات data/, models/, db |
| `cloud_setup.py` | تهيئة Streamlit Cloud (DB، حد الدفعة) |
| `logging_utils.py` | Logger موحّد |

### 3.2 `src/models/`

| الملف | الدور |
|-------|--------|
| `registry.py` | **نقطة الدخول**: `load_predictor()` → BERT |
| `bert_predictor.py` | BERT/XLM-RoBERTa + CAMeLBERT + fine-tuned |
| `finetune_bert.py` | Fine-tune على بيانات المشروع |

**ترتيب BERT عند التحليل:**
1. نموذج fine-tuned محلي (`models/bert_finetuned/`)
2. دمج XLM-RoBERTa + CAMeLBERT للعربي
3. XLM-RoBERTa متعدد اللغات
4. Twitter-RoBERTa للإنجليزي
5. CAMeLBERT للعربي

**شكل النتيجة الموحّد (dict):**
```python
{
  "text", "language", "cleaned_text",
  "sentiment",      # positive | negative | neutral
  "confidence",     # 0–100
  "distribution",   # {negative: %, neutral: %, positive: %}
  "is_reliable",    # True إذا confidence >= threshold
}
```

### 3.3 `src/data/`

| الملف | الدور |
|-------|--------|
| `comment_fetcher.py` | جلب YouTube / Play Store / Reddit (CLI) |
| `loader.py` | قراءة CSV للتدريب |
| `generator.py` | توليد بيانات اصطناعية |
| `astd.py` | دمج مجموعة ASTD العربية |
| `merge_datasets.py` | دمج ملفات CSV |

### 3.4 `src/db/`

| الملف | الدور |
|-------|--------|
| `database.py` | اتصال SQLite + تنفيذ schema.sql |
| `schema.sql` | جداول users, batches, items, alerts |
| `auth.py` | تسجيل دخول، PBKDF2، أدوار |
| `repository.py` | CRUD للدفعات والعناصر |
| `batch_ops.py` | حفظ دفعة تحليل كاملة |

### 3.5 `src/api/`

| الملف | الدور |
|-------|--------|
| `server.py` | FastAPI: `/predict`, `/batch`, `/health` |
| `security.py` | API key اختياري |

### 3.6 `src/analytics/` و `src/evaluation/`

| الملف | الدور |
|-------|--------|
| `keywords.py` | استخراج كلمات مفتاحية |
| `alerts.py` | تنبيهات (نسبة سلبية عالية) |
| `metrics.py` | accuracy, F1, classification report |
| `plots.py` | confusion matrix |
| `explain.py` | LIME لشرح TF-IDF |

### 3.7 `src/reports/`

| الملف | الدور |
|-------|--------|
| `export.py` | تصدير PDF / Excel |

---

## 4. مجلدات التشغيل

| المجلد | الدور |
|--------|--------|
| `scripts/train.py` | تدريب TF-IDF |
| `scripts/evaluate.py` | تقييم على validation |
| `scripts/finetune_bert.py` | Fine-tune BERT |
| `scripts/download_models.py` | تحميل HuggingFace |
| `launchers/` | استدعاء scripts بنفس المعاملات |
| `commands/*.bat` | اختصارات Windows |

---

## 5. شرح بلوكات أساسية (بالتفصيل)

### 5.1 كشف اللغة (`language.py`)

```
نص فارغ → en
لا أحرف عربية → en
عربي + كلمة من SHAMI_HINT_WORDS → ar_shami
عربي بدونها → ar_fusha
```

**لماذا قواعد وليس ML؟** — سريع، شفاف للمناقشة، كافٍ للفصل بين فصحى/شامي في التعليقات القصيرة.

### 5.2 معالجة النص (`preprocessing.py`)

```
إدخال خام
  → استبدال إيموجي برموز (emoji_pos/neg/neu)
  → lowercase (إنجليزي) / normalize_arabic (عربي)
  → إزالة علامات + مسافات زائدة
  → tokenize بالمسافات
  → حذف stopwords + كلمات قصيرة
  → cleaned_text + tokens
```

**ملاحظة:** BERT يستخدم النص الخام غالباً؛ المعالجة مهمة لـ TF-IDF.

### 5.3 TF-IDF (`predictor.py`)

```
تعليق → preprocess → TF-IDF vector → predict_proba
  → أعلى احتمال = sentiment
  → is_reliable = confidence >= 55% (من YAML)
```

**predict_batch:** يجمع كل النصوص الصالحة ويستدعي predict_proba **مرة واحدة** (أسرع).

### 5.4 BERT (`bert_predictor.py`)

```
predict_with_confidence(text, language?)
  → detect_language إن لم تُمرَّر
  → اختيار pipeline حسب اللغة والنماذج المتاحة
  → scores → distribution + sentiment + confidence
  → neutral_threshold: إذا ثقتان منخفضة → neutral
```

**_merge_sentiment_scores:** للعربي يدمج XLM-RoBERTa (55%) + CAMeLBERT (45%).

### 5.5 قاعدة البيانات

```
users ──< analysis_batches ──< analysis_items
                    └──< alerts
```

- **admin:** كل الصلاحيات + إدارة بيانات
- **analyst:** تحليل + حفظ + لوحة
- **viewer:** لوحة + حول فقط (بدون تحليل)

---

## 6. ملفات الإعداد والبيانات

| الملف | المحتوى |
|-------|---------|
| `configs/default.yaml` | datasets, model, training, inference, ui, platform |
| `data/sentiment_dataset_multilingual.csv` | بيانات تدريب |
| `data/validation_comments.csv` | للتقييم (513 عينة) |
| `models/sentiment_model.pkl` | TF-IDF مدرب |
| `models/model_metadata.json` | معلومات التدريب |
| `data/sentiment_platform.db` | SQLite (تُنشأ تلقائياً) |

---

## 7. أوامر مهمة للمناقشة

```powershell
cd sentiment_project
.\run.bat                          # الواجهة http://localhost:8501
pytest tests/ -q                   # 43 اختبار
python scripts/train.py            # تدريب TF-IDF
python scripts/evaluate.py         # مقارنة BERT vs TF-IDF
python docs/generate_graduation_report.py
python docs/generate_presentation.py
```

---

## 8. حالة التعليقات داخل الكود

**تمت إضافة تعليقات عربية لجميع ملفات المشروع (~95 ملف Python + schema.sql + default.yaml + run.bat)**

| المجلد | عدد الملفات | الحالة |
|--------|-------------|--------|
| `app/` + `components/` | 16 | ✅ كامل |
| `src/` | 35+ | ✅ كامل |
| `scripts/` | 15 | ✅ كامل |
| `launchers/` | 18 | ✅ كامل |
| `tests/` | 12 | ✅ كامل |
| `docs/*.py` | 3 | ✅ كامل |
| `configs/default.yaml` | 1 | ✅ كامل |
| `src/db/schema.sql` | 1 | ✅ كامل |
| `run.bat` | 1 | ✅ كامل |

---

*آخر تحديث: مشروع تخرج 2026 — جامعة الشام، قسم الهندسة المعلوماتية*
