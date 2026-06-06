import os

import pandas as pd
import requests

from config import BINANCE_KLINES_URL, DATA_FILE, INTERVAL, SYMBOL, TIMEZONE


def get_previous_completed_minute_end_ms():
    now_utc = pd.Timestamp.now(tz="UTC")

    current_minute_start = now_utc.floor("min")

    previous_minute_end = current_minute_start - pd.Timedelta(milliseconds=1)

    return int(previous_minute_end.timestamp() * 1000)


def fetch_latest_klines(limit=1000):
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


def save_data():
    os.makedirs("data", exist_ok=True)

    df = fetch_latest_klines(limit=1000)

    if os.path.exists(DATA_FILE):
        old_df = pd.read_csv(DATA_FILE)
        old_df["open_time"] = pd.to_datetime(old_df["open_time"])
        old_df["close_time"] = pd.to_datetime(old_df["close_time"])

        df = pd.concat([old_df, df], ignore_index=True)
        df = df.drop_duplicates(subset=["open_time"])
        df = df.sort_values("open_time")

    temp_file = DATA_FILE + ".tmp"
    df.to_csv(temp_file, index=False)
    os.replace(temp_file, DATA_FILE)

    print(f"Saved {len(df)} rows to {DATA_FILE}")
    print(df.tail())


if __name__ == "__main__":
    save_data()
