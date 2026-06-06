import os
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.calibration import calibration_curve
from sklearn.metrics import auc, confusion_matrix, roc_curve

from paths import ProjectPaths


def plot_confusion_matrix(y_true, y_pred, labels: List[str], title: str, out_path: str) -> None:
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels)
    plt.title(title)
    plt.ylabel("True")
    plt.xlabel("Predicted")
    plt.tight_layout()
    plt.savefig(out_path, dpi=180)
    plt.close()


def plot_dataset_distribution(df: pd.DataFrame, out_path: str) -> None:
    counts = df.groupby(["language", "sentiment"]).size().reset_index(name="count")
    plt.figure(figsize=(8, 5))
    sns.barplot(data=counts, x="language", y="count", hue="sentiment")
    plt.title("Dataset distribution by language and sentiment")
    plt.tight_layout()
    plt.savefig(out_path, dpi=180)
    plt.close()


def plot_roc_multiclass(probas, y_true, classes: List[str], out_path: str) -> None:
    y_true = np.array(y_true)
    plt.figure(figsize=(7, 5))
    for index, cls in enumerate(classes):
        y_bin = (y_true == cls).astype(int)
        fpr, tpr, _ = roc_curve(y_bin, probas[:, index])
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, label=f"{cls} (AUC={roc_auc:.3f})")
    plt.plot([0, 1], [0, 1], linestyle="--", color="gray")
    plt.title("ROC Curve (one-vs-rest)")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=180)
    plt.close()


def plot_f1_by_language(per_language: Dict, out_path: str) -> None:
    rows = []
    for lang, report in per_language.items():
        macro = report.get("macro avg", {})
        rows.append({"language": lang, "f1_macro": float(macro.get("f1-score", 0.0))})

    df = pd.DataFrame(rows)
    plt.figure(figsize=(6, 4))
    sns.barplot(data=df, x="language", y="f1_macro")
    plt.ylim(0.0, 1.0)
    plt.title("Macro F1 by language")
    plt.tight_layout()
    plt.savefig(out_path, dpi=180)
    plt.close()


def plot_calibration(probas, y_true, classes: List[str], out_path: str) -> None:
    plt.figure(figsize=(7, 5))
    for index, cls in enumerate(classes):
        y_bin = (np.array(y_true) == cls).astype(int)
        frac_pos, mean_pred = calibration_curve(
            y_bin, probas[:, index], n_bins=10, strategy="uniform"
        )
        plt.plot(mean_pred, frac_pos, marker="o", label=str(cls))

    plt.plot([0, 1], [0, 1], linestyle="--", color="gray")
    plt.title("Calibration plot (one-vs-rest)")
    plt.xlabel("Mean predicted probability")
    plt.ylabel("Fraction of positives")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=180)
    plt.close()
