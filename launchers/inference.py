import os
import sys

_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
_SRC = os.path.abspath(_SRC)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from models.predictor import SentimentPredictor, load_default_predictor  # noqa: F401
