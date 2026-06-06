import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "return_1m",
    "return_3m",
    "return_5m",
    "return_10m",
    "return_15m",
    "price_vs_ma_5",
    "price_vs_ma_10",
    "price_vs_ma_20",
    "price_vs_ma_50",
    "volatility_5",
    "volatility_10",
    "volatility_20",
    "volume_change",
    "trade_change",
]


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["open_time"] = pd.to_datetime(df["open_time"])

    df["return_1m"] = df["close"].pct_change()
    df["return_3m"] = df["close"].pct_change(3)
    df["return_5m"] = df["close"].pct_change(5)
    df["return_10m"] = df["close"].pct_change(10)
    df["return_15m"] = df["close"].pct_change(15)

    df["ma_5"] = df["close"].rolling(5).mean()
    df["ma_10"] = df["close"].rolling(10).mean()
    df["ma_20"] = df["close"].rolling(20).mean()
    df["ma_50"] = df["close"].rolling(50).mean()

    df["price_vs_ma_5"] = (df["close"] - df["ma_5"]) / df["ma_5"]
    df["price_vs_ma_10"] = (df["close"] - df["ma_10"]) / df["ma_10"]
    df["price_vs_ma_20"] = (df["close"] - df["ma_20"]) / df["ma_20"]
    df["price_vs_ma_50"] = (df["close"] - df["ma_50"]) / df["ma_50"]

    df["volatility_5"] = df["return_1m"].rolling(5).std()
    df["volatility_10"] = df["return_1m"].rolling(10).std()
    df["volatility_20"] = df["return_1m"].rolling(20).std()

    df["volume_change"] = df["volume"].pct_change()
    df["trade_change"] = df["number_of_trades"].pct_change()

    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna()

    return df


def create_5_minute_training_rows(df: pd.DataFrame) -> pd.DataFrame:
    df = add_features(df)

    df["minute"] = df["open_time"].dt.minute

    boundary_rows = df[df["minute"] % 5 == 0].copy()

    boundary_rows["base_price"] = boundary_rows["open"]

    # Target close is the close price 5 one-minute candles later.
    boundary_rows["target_close"] = df["close"].shift(-4).loc[boundary_rows.index]

    boundary_rows["target"] = (
        boundary_rows["target_close"] > boundary_rows["base_price"]
    ).astype(int)

    boundary_rows = boundary_rows.dropna()

    return boundary_rows
