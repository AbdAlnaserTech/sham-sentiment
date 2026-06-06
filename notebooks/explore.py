import os
import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = os.path.abspath(os.path.join(os.getcwd(), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

sns.set_theme(style="whitegrid")

train_path = os.path.join(ROOT, "data", "sentiment_dataset_multilingual.csv")
valid_path = os.path.join(ROOT, "data", "real", "validation_comments.csv")

train_df = pd.read_csv(train_path)
valid_df = pd.read_csv(valid_path)

print("Training rows:", len(train_df))
print("Validation rows:", len(valid_df))
train_df.head()
