# BTC Dump - Professional Bitcoin Price Prediction Tool

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

A professional-grade Bitcoin price prediction tool using ensemble machine learning models (XGBoost, Random Forest, and Gradient Boosting) with technical analysis indicators.

---

## Features

* **Ensemble ML Models**: Combines XGBoost, Random Forest, and Gradient Boosting for robust predictions
* **Technical Analysis**: RSI, MACD, Bollinger Bands, Moving Averages
* **Real-time Data**: Fetches live BTC/USDT data from Binance API
* **Multiple Timeframes**: 5min, 30min, 1h, 4h, 1d
* **Live Auto Mode**: Continuous prediction with customizable refresh intervals
* **Visualization**: Interactive price charts with technical indicators
* **Signal Generation**: STRONG BUY/BUY/SELL/STRONG SELL/HOLD signals

---

## Installation

```bash
# Clone the repository
git clone https://github.com/codingcreatively/BTCDump.git
cd BTCDump

# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Basic Usage

```bash
python3 BTCDump.py
```

---

## Menu Options

1. Select Timeframe
2. Train & Predict
3. Show Live Chart
4. Refresh Data Only
5. Show Last Prediction
6. Auto Live Mode
7. Backtesting (Fork Feature)

---

## Technical Analysis Indicators

* Moving Averages: MA5, MA20, MA50
* RSI (14-period)
* MACD (12/26 EMA + 9 signal)
* Bollinger Bands (20 SMA, 2 std dev)
* Volume Analysis

---

## Machine Learning Models

### XGBoost Regressor

* n_estimators: 200
* learning_rate: 0.05
* max_depth: 6

### Random Forest Regressor

* n_estimators: 200
* max_depth: 10
* min_samples_split: 5

### Gradient Boosting Regressor

* n_estimators: 200
* learning_rate: 0.05
* max_depth: 5

---

## Features Used for Prediction

* Price & volume
* RSI, MACD
* Moving averages
* Bollinger Bands
* Volume ratios

---

## Signal Generation Logic

| Condition                   | Signal      |
| --------------------------- | ----------- |
| >1.5% + bullish indicators  | STRONG BUY  |
| >0.5% + moderate bullish    | BUY         |
| <-1.5% + bearish indicators | STRONG SELL |
| <-0.5% + moderate bearish   | SELL        |
| Otherwise                   | HOLD        |

---

## Configuration

### Binance API

```
https://api.binance.com/api/v3/klines
```

No API key required.

---

## Timeframes

| Option | Timeframe |
| ------ | --------- |
| 1      | 5m        |
| 2      | 30m       |
| 3      | 1h        |
| 4      | 4h        |
| 5      | 1d        |

---

## Output Example

```
BTC ANALYSIS
Current Price: $43,250
Prediction: $44,100
Signal: STRONG BUY
```

---

## Architecture

```
BTCPredictorPro
├── fetch_data()
├── indicators()
├── features()
├── train()
├── predict()
├── signal()
├── chart()
├── auto_live()
└── main_menu()
```

---

## Web Dashboard Features (Fork by @johnoszwa)

* Real-time price updates
* Interactive charts (Plotly)
* Portfolio manager
* Risk meter
* Signal dashboard
* Trade log
* Technical indicators (ADX, RSI, MACD)
* Mobile responsive

---

## Backtesting

Run via menu option 7.

Includes:

* ROI
* Win rate
* Trade count
* Final balance

---

## Advanced Architecture (v3.0)

```
BTCDump Pro
├── Core (alexxx)
├── Enhancements (@johnoszwa)
│   ├── Risk Manager
│   ├── Backtesting
│   ├── Web Dashboard
│   └── Advanced Indicators
```

---

## Performance

* Error: 1–3% MAPE
* Speed: <1s prediction
* Training: 10–30s

---

## Logging

Logs saved as:

```
trading_bot_YYYYMMDD.log
```

---

## Project Structure

```
BTCDump/
├── BTCDump.py
├── app.py
├── app_offline.py
├── app_simple.py
├── requirements.txt
├── README.md
```

---

## Disclaimer

⚠️ Educational use only.

* High risk trading
* No guarantees
* No liability

---

## Authors

* Original: alexxx
* Fork: @johnoszwa

---

## Contributing

1. Fork repo
2. Create branch
3. Commit changes
4. Push
5. Open PR

---

## License

MIT License

---

## 📁 Available Versions

| File             | Description            | Use Case                             |
| ---------------- | ---------------------- | ------------------------------------ |
| `BTCDump.py`     | Full terminal version  | Original CLI interface               |
| `app.py`         | Complete web dashboard | Full features, needs internet        |
| `app_offline.py` | Offline demo mode      | No internet required, simulated data |
| `app_simple.py`  | Lightweight web UI     | Slow connections, basic features     |

### Quick Start Examples:

```bash
# Offline demo (no internet needed)
python app_offline.py

# Lightweight version (good for slow connections)
python app_simple.py

# Full version (requires internet)
python app.py

# Terminal version
python BTCDump.py
```

---

**BTC Dump Pro v3.0**
