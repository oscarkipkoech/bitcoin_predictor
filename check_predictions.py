import os
import time

import pandas as pd
import requests

from config import (
    BINANCE_KLINES_URL,
    CHECK_EVERY_SECONDS,
    PREDICTIONS_FILE,
    SYMBOL,
    TIMEZONE,
)


def fetch_1m_candle_by_time(target_time):
    """
    Fetch the 1-minute candle that opened exactly at target_time.
    For our check, we use the close price of that 1-minute candle.
    """

    target_time = pd.Timestamp(target_time)

    if target_time.tzinfo is None:
        target_time = target_time.tz_localize(TIMEZONE)
    else:
        target_time = target_time.tz_convert(TIMEZONE)

    start_ms = int(target_time.tz_convert("UTC").timestamp() * 1000)
    end_ms = start_ms + 60_000

    params = {
        "symbol": SYMBOL,
        "interval": "1m",
        "startTime": start_ms,
        "endTime": end_ms,
        "limit": 1,
    }

    response = requests.get(BINANCE_KLINES_URL, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    if not data:
        return None

    candle = data[0]

    return {
        "open_time": pd.to_datetime(candle[0], unit="ms", utc=True).tz_convert(
            TIMEZONE
        ),
        "open": float(candle[1]),
        "high": float(candle[2]),
        "low": float(candle[3]),
        "close": float(candle[4]),
        "close_time": pd.to_datetime(candle[6], unit="ms", utc=True).tz_convert(
            TIMEZONE
        ),
    }


def check_predictions():
    if not os.path.exists(PREDICTIONS_FILE):
        print(f"No predictions file found: {PREDICTIONS_FILE}")
        return

    df = pd.read_csv(
        PREDICTIONS_FILE,
        dtype={"prediction": str, "actual_result": str, "was_correct": str},
    )
    for column in ["actual_result", "prediction", "was_correct"]:
        df[column] = df[column].astype("object")
    required_columns = [
        "base_time",
        "target_time",
        "base_price",
        "prediction",
        "actual_close_at_target",
        "actual_result",
        "was_correct",
    ]

    for column in required_columns:
        if column not in df.columns:
            df[column] = ""

    now = pd.Timestamp.now(tz=TIMEZONE)

    checked_count = 0

    for index, row in df.iterrows():
        if str(row.get("was_correct", "")).strip() not in ["", "nan", "None"]:
            continue

        target_time = pd.Timestamp(row["target_time"])

        if target_time.tzinfo is None:
            target_time = target_time.tz_localize(TIMEZONE)
        else:
            target_time = target_time.tz_convert(TIMEZONE)

        # Wait until the target candle has closed.
        # Example: target_time 21:30 means the 21:30 one-minute candle
        # should be available after 21:31.
        if now < target_time + pd.Timedelta(minutes=1):
            continue

        candle = fetch_1m_candle_by_time(target_time)

        if candle is None:
            continue

        base_price = float(row["base_price"])
        actual_close = candle["close"]

        actual_result = "UP" if actual_close > base_price else "DOWN"
        was_correct = actual_result == row["prediction"]

        df.at[index, "actual_close_at_target"] = round(actual_close, 2)
        df.at[index, "actual_result"] = actual_result
        df.at[index, "was_correct"] = was_correct

        checked_count += 1

    df.to_csv(PREDICTIONS_FILE, index=False)

    total_checked = df[df["was_correct"].astype(str).isin(["True", "False"])]

    if len(total_checked) > 0:
        accuracy = (total_checked["was_correct"].astype(str) == "True").mean() * 100
    else:
        accuracy = 0

    print("=" * 60)
    print(f"Checked new predictions: {checked_count}")
    print(f"Total checked predictions: {len(total_checked)}")
    print(f"Accuracy: {accuracy:.2f}%")
    print("=" * 60)


if __name__ == "__main__":
    while True:
        try:
            check_predictions()
        except Exception as e:
            import traceback

            traceback.print_exc()

        time.sleep(CHECK_EVERY_SECONDS)
