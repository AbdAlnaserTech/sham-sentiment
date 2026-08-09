"""
حزمة data — إعداد ومعالجة وجلب بيانات تحليل المشاعر.

الوحدات:
  - loader          : تحميل CSV موسوم
  - generator       : توليد بيانات اصطناعية متعددة اللغات
  - astd            : تنزيل ومعالجة مجموعة ASTD العربية
  - merge_datasets  : دمج البيانات الاصطناعية + ASTD مع فصل التحقق
  - build_validation: توسيع ملف التحقق (~108 عينة)
  - comment_fetcher : جلب تعليقات حقيقية من YouTube / Google Play / Reddit
"""
