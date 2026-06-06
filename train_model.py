import os

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

from config import DATA_FILE, MODEL_FILE
from features import FEATURE_COLUMNS, create_5_minute_training_rows


def train():
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError("No data file found. Run collect_loop.py first.")

    df = pd.read_csv(DATA_FILE)

    df["open_time"] = pd.to_datetime(df["open_time"])
    df["close_time"] = pd.to_datetime(df["close_time"])

    df = create_5_minute_training_rows(df)

    if len(df) < 200:
        raise ValueError(f"Not enough training rows yet. Current rows: {len(df)}")

    X = df[FEATURE_COLUMNS]
    y = df["target"]

    split_index = int(len(df) * 0.8)

    X_train = X.iloc[:split_index]
    y_train = y.iloc[:split_index]

    X_test = X.iloc[split_index:]
    y_test = y.iloc[split_index:]

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)

    print(f"Rows used: {len(df)}")
    print(f"Test accuracy: {accuracy * 100:.2f}%")
    print(classification_report(y_test, predictions))

    os.makedirs("models", exist_ok=True)

    temp_model_file = MODEL_FILE + ".tmp"
    joblib.dump(model, temp_model_file)
    os.replace(temp_model_file, MODEL_FILE)

    print(f"Model saved to {MODEL_FILE}")


if __name__ == "__main__":
    train()
