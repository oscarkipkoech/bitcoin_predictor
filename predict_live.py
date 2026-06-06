import os
import time
from datetime import datetime, timedelta

import joblib
import pandas as pd
import requests

from config import (
    BINANCE_KLINES_URL,
    INTERVAL,
    LIVE_RUN_EVERY_SECONDS,
    MODEL_FILE,
    PREDICTIONS_FILE,
    SYMBOL,
    TIMEZONE,
)
from features import FEATURE_COLUMNS, add_features


def floor_to_5_minute(dt):
    minute = (dt.minute // 5) * 5
    return dt.replace(minute=minute, second=0, microsecond=0)


def get_previous_completed_minute_end_ms():
    now_utc = pd.Timestamp.now(tz="UTC")

    current_minute_start = now_utc.floor("min")

    previous_minute_end = current_minute_start - pd.Timedelta(milliseconds=1)

    return int(previous_minute_end.timestamp() * 1000)


def fetch_recent_data(limit=300):
    end_time_ms = get_previous_completed_minute_end_ms()

    params = {
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "limit": limit,
        "endTime": end_time_ms,
    }

    response = requests.get(BINANCE_KLINES_URL, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    df = pd.DataFrame(
        data,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base_volume",
            "taker_buy_quote_volume",
            "ignore",
        ],
    )

    df["open_time"] = pd.to_datetime(
        df["open_time"], unit="ms", utc=True
    ).dt.tz_convert(TIMEZONE)
    df["close_time"] = pd.to_datetime(
        df["close_time"], unit="ms", utc=True
    ).dt.tz_convert(TIMEZONE)

    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "quote_asset_volume",
        "number_of_trades",
        "taker_buy_base_volume",
        "taker_buy_quote_volume",
    ]

    df[numeric_columns] = df[numeric_columns].astype(float)

    return df


def save_prediction(row):
    os.makedirs("predictions", exist_ok=True)

    new_df = pd.DataFrame([row])

    if os.path.exists(PREDICTIONS_FILE):
        old_df = pd.read_csv(PREDICTIONS_FILE)

        # Avoid saving duplicate predictions for the same base and target window.
        old_df = old_df[
            ~(
                (old_df["base_time"] == row["base_time"])
                & (old_df["target_time"] == row["target_time"])
            )
        ]

        new_df = pd.concat([old_df, new_df], ignore_index=True)

    new_df.to_csv(PREDICTIONS_FILE, index=False)


def predict_once():
    if not os.path.exists(MODEL_FILE):
        raise FileNotFoundError("No trained model found. Run train_model.py first.")

    model = joblib.load(MODEL_FILE)

    raw_df = fetch_recent_data(limit=300)
    df = add_features(raw_df)

    now = pd.Timestamp.now(tz=TIMEZONE)

    latest_available_time = df["open_time"].max()

    base_time = floor_to_5_minute(latest_available_time)
    target_time = base_time + timedelta(minutes=5)

    base_row = df[df["open_time"] == base_time]

    if base_row.empty:
        print(f"No candle found yet for base time {base_time}")
        return

    latest = base_row.iloc[0]

    latest_features = latest[FEATURE_COLUMNS].to_frame().T

    probability_up = model.predict_proba(latest_features)[0][1]
    probability_down = 1 - probability_up

    prediction = "UP" if probability_up >= 0.5 else "DOWN"
    confidence = abs(probability_up - 0.5) * 2

    base_price = latest["open"]

    result = {
        "created_at": str(now),
        "base_time": str(base_time),
        "target_time": str(target_time),
        "base_price": round(base_price, 2),
        "prediction": prediction,
        "probability_up": round(probability_up * 100, 2),
        "probability_down": round(probability_down * 100, 2),
        "confidence_level": round(confidence * 100, 2),
        "actual_close_at_target": "",
        "actual_result": "",
        "was_correct": "",
    }

    save_prediction(result)

    print("=" * 70)
    print(f"Current time: {now.strftime('%H:%M:%S')}")
    print(f"Latest completed 1m candle: {latest_available_time.strftime('%H:%M')}")
    print(f"Price at {base_time.strftime('%H:%M')}: {base_price:.2f}")
    print(f"Target close time: {target_time.strftime('%H:%M')}")
    print(
        f"Possibility UP at {target_time.strftime('%H:%M')}: {probability_up * 100:.2f}%"
    )
    print(
        f"Possibility DOWN at {target_time.strftime('%H:%M')}: {probability_down * 100:.2f}%"
    )
    print(f"Prediction: {prediction}")
    print(f"Confidence level: {confidence * 100:.2f}%")
    print("=" * 70)


if __name__ == "__main__":
    while True:
        try:
            predict_once()
        except Exception as e:
            print(f"Error: {e}")

        time.sleep(LIVE_RUN_EVERY_SECONDS)
