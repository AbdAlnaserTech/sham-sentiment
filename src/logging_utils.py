"""أدوات التسجيل (logging) وحفظ/تحميل ملفات JSON للمشروع."""

import json
import logging
from typing import Any, Dict

# اسم المسجّل الرئيسي للمشروع
LOGGER_NAME = "sentiment_project"


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """إعداد مسجّل وحيد بمخرجات إلى الطرفية."""
    logger = logging.getLogger(LOGGER_NAME)
    if logger.handlers:
        return logger

    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )
    logger.addHandler(handler)
    return logger


# مسجّل جاهز للاستخدام في بقية المشروع
logger = setup_logging()


def save_json(path: str, obj: Dict[str, Any]) -> None:
    """حفظ قاموس Python كملف JSON بترميز UTF-8."""
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(obj, handle, ensure_ascii=False, indent=2)


def load_json(path: str) -> Dict[str, Any]:
    """تحميل ملف JSON وإرجاعه كقاموس."""
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)
