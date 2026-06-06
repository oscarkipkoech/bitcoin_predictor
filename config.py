SYMBOL = "BTCUSDT"
INTERVAL = "1m"

TIMEZONE = "Africa/Nairobi"

DATA_FILE = "data/btc_1m_data.csv"
MODEL_FILE = "models/btc_direction_model.pkl"
PREDICTIONS_FILE = "predictions/live_predictions.csv"

BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"

PREDICTION_HORIZON_MINUTES = 5
LIVE_RUN_EVERY_SECONDS = 10

COLLECT_EVERY_SECONDS = 60
TRAIN_EVERY_SECONDS = 15 * 60
CHECK_EVERY_SECONDS = 20
LIVE_RUN_EVERY_SECONDS = 10
