import sys
import os

_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from augmentation import (  # noqa: F401
    OptionalAugmenters,
    Paraphraser,
    add_social_flavor,
    normalize_elongation,
    synonym_replace,
)
