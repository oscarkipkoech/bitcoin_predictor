# Bitcoin Predictor Project Session Notes

## Project Overview

This project predicts the direction of Bitcoin over fixed 5-minute windows using Binance market data and a machine learning model.

The system is intended for experimentation and learning. It is not currently a production trading system.

Current market:

```txt
BTCUSDT
```

Data source:

```txt
Binance Spot API
```

Primary timezone:

```txt
Africa/Nairobi (UTC+3)
```

## User Requirements

The user explicitly requested that predictions follow fixed 5-minute boundaries.

Examples:

```txt
21:24
Base time = 21:20
Target time = 21:25
```

```txt
21:27
Base time = 21:25
Target time = 21:30
```

Prediction should always compare:

```txt
Target close price
vs
Base price
```

The output format should resemble:

```txt
Price at 21:25: 104500

Possibility UP at 21:30: 67%
Possibility DOWN at 21:30: 33%

Confidence level: 34%
```

This requirement supersedes earlier versions that predicted simply 5 minutes ahead from the latest candle.

## Architecture

Current architecture uses four continuously running processes.

Terminal 1:

```txt
collect_loop.py
```

Terminal 2:

```txt
train_loop.py
```

Terminal 3:

```txt
predict_live.py
```

Terminal 4:

```txt
check_predictions.py
```

## File Structure

```txt
bitcoin_predictor/
│
├── data/
│   └── btc_1m_data.csv
│
├── models/
│   └── btc_direction_model.pkl
│
├── predictions/
│   └── live_predictions.csv
│
├── config.py
├── features.py
├── collect_data.py
├── collect_loop.py
├── train_model.py
├── train_loop.py
├── predict_live.py
├── check_predictions.py
├── README.md
└── session_gpt.md
```

## Current Data Source

Endpoint:

```txt
https://api.binance.com/api/v3/klines
```

Current interval:

```txt
1m
```

Current symbol:

```txt
BTCUSDT
```

Reason:

Using 1-minute candles provides more information than 5-minute candles while still allowing predictions on fixed 5-minute boundaries.

## Current Training Strategy

Current model:

```txt
LogisticRegression
```

Training rows are generated from 1-minute candles.

Only candles beginning on 5-minute boundaries are used for training targets.

Example:

```txt
21:25
```

Target:

```txt
Will close at 21:30 be higher than open at 21:25?
```

Target variable:

```python
target = target_close > base_price
```

Output:

```txt
1 = UP
0 = DOWN
```

## Current Features

Features currently used:

```txt
return_1m
return_3m
return_5m
return_10m
return_15m

price_vs_ma_5
price_vs_ma_10
price_vs_ma_20
price_vs_ma_50

volatility_5
volatility_10
volatility_20

volume_change
trade_change
```

## Retraining Strategy

Current retraining frequency:

```txt
Every 15 minutes
```

Current data collection frequency:

```txt
Every 60 seconds
```

Current prediction frequency:

```txt
Every 10 seconds
```

Current prediction validation frequency:

```txt
Every 20 seconds
```

## Prediction Validation

Predictions are stored in:

```txt
predictions/live_predictions.csv
```

After the target time passes:

```txt
check_predictions.py
```

fetches actual Binance candle data and records:

```txt
actual_close_at_target
actual_result
was_correct
```

This creates a growing historical record of model performance.

## Known Issues

### CSV file lock

If a CSV file is opened in Excel:

```txt
PermissionError: [Errno 13]
```

may occur.

Recommendation:

Never open active CSV files while loops are running.

Use copied files instead.

### Old prediction schema

Older versions created prediction files without:

```txt
base_time
target_time
```

This caused:

```txt
Error: 'base_time'
```

Deleting the old prediction file fixes the issue.

## Future Improvements

### High Priority

Replace Logistic Regression with:

```txt
RandomForest
XGBoost
LightGBM
```

Compare results against baseline.

### High Priority

Store data in SQLite instead of CSV.

Potential future file:

```txt
database.db
```

Benefits:

* No file locking issues
* Easier analytics
* Easier historical queries

### High Priority

Create dashboard.py

Dashboard should display:

```txt
Current BTC price
Current prediction
Current confidence

Total predictions

Accuracy today
Accuracy last 100
Accuracy last 500
Accuracy last 1000
```

### Medium Priority

Predict:

```txt
Expected percentage move
```

instead of only:

```txt
UP / DOWN
```

Desired future output:

```txt
Price at 21:25: 104500

Expected close:
104720

Expected move:
+0.21%

Possibility UP:
67%

Possibility DOWN:
33%

Confidence:
34%
```

### Medium Priority

Add technical indicators:

```txt
RSI
MACD
ATR
Bollinger Bands
VWAP
```

### Medium Priority

Train on rolling window:

```txt
Last 30 days only
```

Approximately:

```txt
43,200
```

one-minute candles.

## Run Order

Recommended startup order:

```txt
1. collect_loop.py
2. train_loop.py
3. predict_live.py
4. check_predictions.py
```

Shutdown:

```txt
CTRL + C
```

in each terminal.

## Important Notes For Future AI Sessions

Do not change the fixed 5-minute boundary prediction logic unless specifically requested.

The user intentionally rejected a simple "predict 5 minutes from now" approach.

Predictions must always align to:

```txt
00
05
10
15
20
25
30
35
40
45
50
55
```

minute boundaries.

Timezone should remain:

```txt
Africa/Nairobi
```

unless the user explicitly requests otherwise.

Future improvements should focus on measurable prediction accuracy, not more sophisticated-looking output.

Accuracy tracking and backtesting are more important than confidence percentages.
