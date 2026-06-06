"""Fine-tune XLM-RoBERTa on project data to improve real-world accuracy."""

import argparse
import os
import sys

_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)
import bootstrap  # noqa: E402

_ROOT = bootstrap.ROOT

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import accuracy_score, f1_score  # noqa: E402

from logging_utils import logger, save_json  # noqa: E402
from paths import ProjectPaths  # noqa: E402

BASE_MODEL = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
LABEL2ID = {"negative": 0, "neutral": 1, "positive": 2}
ID2LABEL = {v: k for k, v in LABEL2ID.items()}


def _balance_training_frame(train_df: pd.DataFrame, max_samples: int) -> pd.DataFrame:
    """Oversample minority classes so neutral/negative/positive are balanced."""
    train_df = train_df[train_df["sentiment"].isin(LABEL2ID)].copy()
    if train_df.empty:
        return train_df

    per_class = max(200, max_samples // 3) if max_samples else None
    parts = []
    for label in LABEL2ID:
        subset = train_df[train_df["sentiment"] == label]
        if subset.empty:
            continue
        target = min(len(subset), per_class) if per_class else len(subset)
        parts.append(subset.sample(n=target, replace=len(subset) < target, random_state=42))

    balanced = pd.concat(parts, ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)
    if max_samples and len(balanced) > max_samples:
        per_group = max(1, max_samples // 3)
        parts = []
        for label in LABEL2ID:
            group = balanced[balanced["sentiment"] == label]
            if group.empty:
                continue
            parts.append(
                group.sample(
                    n=min(len(group), per_group),
                    replace=len(group) < per_group,
                    random_state=42,
                )
            )
        balanced = pd.concat(parts, ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)
    return balanced


def _class_weights_tensor(train_df: pd.DataFrame):
    import torch

    counts = train_df["labels"].value_counts().to_dict()
    total = len(train_df)
    weights = []
    for label_id in range(3):
        count = counts.get(label_id, 1)
        weights.append(total / (3.0 * count))
    return torch.tensor(weights, dtype=torch.float)


def finetune(
    train_path: str,
    val_path: str,
    root_dir: str | None = None,
    epochs: int = 2,
    max_samples: int = 0,
    batch_size: int = 8,
) -> dict:
    try:
        import torch
        from torch import nn
        from transformers import (
            AutoModelForSequenceClassification,
            AutoTokenizer,
            Trainer,
            TrainingArguments,
        )
    except ImportError as exc:
        raise SystemExit("Install: pip install -r requirements_bert.txt") from exc

    paths = ProjectPaths.from_project_root(root_dir or _ROOT)
    out_dir = os.path.join(paths.models_dir, "bert_finetuned")
    os.makedirs(out_dir, exist_ok=True)

    train_df = pd.read_csv(train_path).dropna(subset=["text", "sentiment"])
    val_df = pd.read_csv(val_path).dropna(subset=["text", "sentiment"])
    train_df = _balance_training_frame(train_df, max_samples)
    val_df = val_df[val_df["sentiment"].isin(LABEL2ID)]

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL,
        num_labels=3,
        id2label=ID2LABEL,
        label2id=LABEL2ID,
    )

    def tokenize(batch):
        return tokenizer(batch["text"], truncation=True, max_length=128, padding="max_length")

    train_t = train_df.rename(columns={"sentiment": "labels"})
    val_t = val_df.rename(columns={"sentiment": "labels"})
    train_t["labels"] = train_t["labels"].map(LABEL2ID)
    val_t["labels"] = val_t["labels"].map(LABEL2ID)

    class_weights = _class_weights_tensor(train_t)

    from datasets import Dataset

    train_ds = Dataset.from_pandas(train_t[["text", "labels"]])
    val_ds = Dataset.from_pandas(val_t[["text", "labels"]])
    train_ds = train_ds.map(tokenize, batched=True)
    val_ds = val_ds.map(tokenize, batched=True)
    cols = ["input_ids", "attention_mask", "labels"]
    train_ds = train_ds.remove_columns([c for c in train_ds.column_names if c not in cols])
    val_ds = val_ds.remove_columns([c for c in val_ds.column_names if c not in cols])

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        preds = np.argmax(logits, axis=1)
        return {
            "accuracy": accuracy_score(labels, preds),
            "f1_macro": f1_score(labels, preds, average="macro"),
        }

    class WeightedTrainer(Trainer):
        def __init__(self, *args, class_weights=None, **kwargs):
            super().__init__(*args, **kwargs)
            self.class_weights = class_weights

        def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
            labels = inputs.pop("labels")
            outputs = model(**inputs)
            weight = self.class_weights.to(model.device)
            loss_fn = nn.CrossEntropyLoss(weight=weight)
            loss = loss_fn(outputs.logits, labels)
            return (loss, outputs) if return_outputs else loss

    use_gpu = torch.cuda.is_available()
    args = TrainingArguments(
        output_dir=out_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",
        greater_is_better=True,
        save_total_limit=1,
        logging_steps=25,
        learning_rate=2e-5,
        weight_decay=0.01,
        warmup_ratio=0.1,
        report_to=[],
        fp16=use_gpu,
    )

    trainer = WeightedTrainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        compute_metrics=compute_metrics,
        class_weights=class_weights,
    )

    logger.info("Fine-tuning BERT on %d balanced samples (%d epochs)...", len(train_df), epochs)
    trainer.train()
    metrics = trainer.evaluate()
    trainer.save_model(out_dir)
    tokenizer.save_pretrained(out_dir)

    report = {
        "base_model": BASE_MODEL,
        "train_samples": len(train_df),
        "val_samples": len(val_df),
        "epochs": epochs,
        "class_weights": class_weights.tolist(),
        "eval_accuracy": float(metrics.get("eval_accuracy", 0)),
        "eval_f1_macro": float(metrics.get("eval_f1_macro", 0)),
        "model_dir": out_dir,
    }
    save_json(os.path.join(out_dir, "finetune_report.json"), report)
    save_json(os.path.join(paths.reports_dir, "bert_finetune_report.json"), report)
    logger.info("Fine-tune F1=%.4f Acc=%.4f", report["eval_f1_macro"], report["eval_accuracy"])
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", default="data/combined_training.csv")
    parser.add_argument("--validation", default="data/real/validation_comments.csv")
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--max-samples", type=int, default=2400, help="Balanced training cap")
    parser.add_argument("--batch-size", type=int, default=8)
    args = parser.parse_args()

    train_path = args.train if os.path.isabs(args.train) else os.path.join(_ROOT, args.train)
    val_path = args.validation if os.path.isabs(args.validation) else os.path.join(_ROOT, args.validation)

    report = finetune(
        train_path,
        val_path,
        epochs=args.epochs,
        max_samples=args.max_samples,
        batch_size=args.batch_size,
    )
    print(f"Fine-tuned model saved: {report['model_dir']}")
    print(f"Validation F1: {report['eval_f1_macro']:.4f} | Acc: {report['eval_accuracy']:.4f}")


if __name__ == "__main__":
    main()
