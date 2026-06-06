"""Download HuggingFace models required for BERT mode."""

import argparse
import os
import sys

_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)
import bootstrap  # noqa: E402

_ROOT = bootstrap.ROOT

from models.bert_predictor import AR_MODEL, EN_MODEL, MULTI_MODEL  # noqa: E402


def download_model(model_id: str) -> str:
    from huggingface_hub import snapshot_download

    print(f"Downloading {model_id} ...")
    path = snapshot_download(
        repo_id=model_id,
        resume_download=True,
    )
    print(f"  -> cached at {path}")
    return path


def verify_model(model_id: str) -> bool:
    from huggingface_hub import snapshot_download

    try:
        path = snapshot_download(repo_id=model_id, local_files_only=True)
    except Exception:
        return False

    files = os.listdir(path) if os.path.isdir(path) else []
    has_weights = any(
        name.endswith((".bin", ".safetensors"))
        for name in files
    )
    print(f"{model_id}: {'OK' if has_weights else 'INCOMPLETE'} ({len(files)} files)")
    return has_weights


def main() -> None:
    parser = argparse.ArgumentParser(description="Download BERT/CAMeLBERT models")
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()

    models = [MULTI_MODEL, EN_MODEL, AR_MODEL]

    if args.verify_only:
        ok = all(verify_model(model_id) for model_id in models)
        raise SystemExit(0 if ok else 1)

    for model_id in models:
        download_model(model_id)
        verify_model(model_id)

    print("\nAll models ready. Run: python compare_models.py --quick")


if __name__ == "__main__":
    main()
