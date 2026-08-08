# Scripts — أدوات سطر الأوامر

كل أدوات المشروع التشغيلية التنفيذية هنا. الواجهات القديمة انتقلت إلى [launchers/](../launchers):

```bash
python scripts/train.py
python scripts/evaluate.py
python scripts/compare_models.py
```

## المجموعات

### 1) التدريب والتحليل

| الملف | الوظيفة |
|-------|---------|
| `train.py` | تدريب نموذج TF-IDF |
| `evaluate.py` | تقييم على CSV موسوم |
| `analyze.py` | تحليل من الطرفية |
| `compare_models.py` | مقارنة TF-IDF vs BERT |
| `compare_algorithms.py` | مقارنة 6 خوارزميات + حفظ الأفضل |

### 2) تجهيز البيانات

| الملف | الوظيفة |
|-------|---------|
| `prepare_data.py` | دمج بيانات التدريب + validation |
| `expand_validation.py` | توسيع مجموعة الاختبار |
| `generate_dataset.py` | توليد بيانات مصنّعة |
| `download_astd.py` | تحميل dataset ASTD |
| `download_models.py` | تحميل نماذج HuggingFace |
| `fetch_comments.py` | جلب تعليقات YouTube / Google Play / Reddit |

### 3) النماذج والخدمات

| الملف | الوظيفة |
|-------|---------|
| `finetune_bert.py` | Fine-tune BERT (اختياري) |
| `run_api.py` | تشغيل FastAPI |

### 4) ملفات مساعدة

| الملف | الوظيفة |
|-------|---------|
| `bootstrap.py` | إعداد المسارات (لا تشغّله مباشرة) |

> إذا كنت تريد مساراً أبسط للتشغيل من جذر المشروع، استخدم ملفات [launchers/](../launchers) التي تعيد التوجيه إلى هذه السكربتات.

