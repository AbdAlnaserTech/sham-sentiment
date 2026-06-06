# Scripts — أدوات سطر الأوامر

كل أدوات المشروع التشغيلية هنا. من جذر المشروع يمكنك تشغيلها بنفس الاسم:

```bash
python train.py          # = python scripts/train.py
python evaluate.py
python compare_models.py
```

| الملف | الوظيفة |
|-------|---------|
| `train.py` | تدريب نموذj TF-IDF |
| `compare_algorithms.py` | مقارنة 6 خوارزmيات + حفظ الأفضل |
| `compare_models.py` | مقارنة TF-IDF vs BERT |
| `evaluate.py` | تقييم على CSV موسوم |
| `analyze.py` | تحليل من الطرفية |
| `prepare_data.py` | دمج بيانات التدريb + validation |
| `expand_validation.py` | توسيع مجموعة الاختبار |
| `finetune_bert.py` | Fine-tune BERT (اختياري) |
| `download_models.py` | تحميل نماذj HuggingFace |
| `download_astd.py` | تحميل dataset ASTD |
| `generate_dataset.py` | توليد بيانات مصنّعة |
| `fetch_comments.py` | جلب تعليقات YouTube / Google Play / Reddit |
| `run_api.py` | تشغيل FastAPI |

`bootstrap.py` — إعداد المسارات (لا تشغّله مباشرة).
