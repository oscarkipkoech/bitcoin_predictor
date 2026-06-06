# Bitcoin 5-minute direction predictor

This project collects Bitcoin price data from Binance, trains a simple machine learning model, predicts whether the next fixed 5-minute candle will close UP or DOWN, and checks whether previous predictions were correct.

## Prediction logic

The prediction is based on fixed 5-minute windows.

Examples:

- If current time is 21:24, the base time is 21:20 and the target time is 21:25.
- If current time is 21:27, the base time is 21:25 and the target time is 21:30.
- The prediction checks whether the target close price will be higher or lower than the base price.

The base price is the open price of the latest 5-minute boundary candle.

## Project structure

```txt
bitcoin_predictor/
├── data/
│   └── btc_1m_data.csv
├── models/
│   └── btc_direction_model.pkl
├── predictions/
│   └── live_predictions.csv
├── config.py
├── features.py
├── collect_data.py
├── train_model.py
├── predict_live.py
└── check_predictions.py
# Running the application

Open 4 separate terminals.

## Terminal 1 - Data collection

This downloads the latest Binance data every minute and updates the local dataset.

```bash
cd E:\python\bitcoin_predictor
venv\Scripts\activate

python collect_loop.py
```

Expected output:

```txt
Collecting latest BTC data...
Saved 1450 rows to data/btc_1m_data.csv
```

---

## Terminal 2 - Model training

This retrains the model every 15 minutes using the latest collected data.

```bash
cd E:\python\bitcoin_predictor
venv\Scripts\activate

python train_loop.py
```

Expected output:

```txt
Training model...
Rows used: 1250
Test accuracy: 54.32%
Model saved to models/btc_direction_model.pkl
```

---

## Terminal 3 - Live predictions

This generates predictions every few seconds.

```bash
cd E:\python\bitcoin_predictor
venv\Scripts\activate

python predict_live.py
```

Expected output:

```txt
Current time: 21:27:12
Price at 21:25: 68460.20
Target close time: 21:30
Possibility UP at 21:30: 51.80%
Possibility DOWN at 21:30: 48.20%
Prediction: UP
Confidence level: 3.60%
```

---

## Terminal 4 - Prediction checker

This checks completed predictions and calculates accuracy.

```bash
cd E:\python\bitcoin_predictor
venv\Scripts\activate

python check_predictions.py
```

Expected output:

```txt
Checked new predictions: 5
Total checked predictions: 120
Accuracy: 54.17%
```

---

# First time setup

Run these commands once:

```bash
cd E:\python\bitcoin_predictor

venv\Scripts\activate

python collect_data.py
python train_model.py
```

After those complete successfully, start the four terminals:

```bash
python collect_loop.py
python train_loop.py
python predict_live.py
python check_predictions.py
```

---

# Stopping the application

In each terminal:

```txt
CTRL + C
```

---

# Recommended daily workflow

Start in this order:

```txt
1. collect_loop.py
2. train_loop.py
3. predict_live.py
4. check_predictions.py
```

Wait until at least one successful training cycle completes before relying on predictions.

---

# Important note

Do not open the following files directly in Excel while the application is running:

```txt
data/btc_1m_data.csv
predictions/live_predictions.csv
```

Excel locks the files and can cause:

```txt
PermissionError: [Errno 13] Permission denied
```

If you want to inspect the data, first make a copy:

```bash
copy data\btc_1m_data.csv data\btc_1m_data_copy.csv
copy predictions\live_predictions.csv predictions\live_predictions_copy.csv
```
