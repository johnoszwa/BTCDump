import os
import time
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
from collections import deque
import json
import logging
from functools import lru_cache
import warnings
warnings.filterwarnings("ignore")

# ===================== SETUP LOGGING =====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'trading_bot_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

# ===================== BANNER =====================
BANNER = r"""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║  ██████╗ ██╗   ██╗███╗   ███╗██████╗     ██████╗ ████████╗ ██████╗ ║
║  ██╔══██╗██║   ██║████╗ ████║██╔══██╗    ██╔══██╗╚══██╔══╝██╔════╝ ║
║  ██║  ██║██║   ██║██╔████╔██║██████╔╝    ██████╔╝   ██║   ██║      ║
║  ██║  ██║██║   ██║██║╚██╔╝██║██╔═══╝     ██╔══██╗   ██║   ██║      ║
║  ██████╔╝╚██████╔╝██║ ╚═╝ ██║██║         ██████╔╝   ██║   ╚██████╗ ║
║  ╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚═╝         ╚═════╝    ╚═╝    ╚═════╝ ║
║                                                                    ║
╠════════════════════════════════════════════════════════════════════╣
║  TOOL      : DUMP BTC PRO EDITION                                  ║
║  AUTHOR    : alexxx                                                ║
║  VERSION   : 3.0 (Enhanced)                                        ║
╚════════════════════════════════════════════════════════════════════╝
"""

BINANCE_API = "https://api.binance.com/api/v3/klines"

TIMEFRAMES = {
    "1": ("5m", "5 Minutes"),
    "2": ("30m", "30 Minutes"),
    "3": ("1h", "1 Hour"),
    "4": ("4h", "4 Hours"),
    "5": ("1d", "1 Day")
}

WHITE = "\033[97m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# ===================== RISK MANAGER CLASS =====================
class RiskManager:
    def __init__(self, initial_capital=1000):
        self.capital = initial_capital
        self.max_risk_per_trade = 0.02  # 2% risk per trade
        self.max_daily_risk = 0.06
        self.daily_loss = 0
        self.consecutive_losses = 0
        self.trades_today = 0
        self.trade_history = []
        
    def set_portfolio_amount(self, new_amount):
        """Change portfolio amount dynamically"""
        if new_amount > 0:
            old_amount = self.capital
            self.capital = new_amount
            logging.info(f"Portfolio updated: ${old_amount:.2f} → ${new_amount:.2f}")
            return True
        return False

    def get_portfolio_info(self):
        """Get detailed portfolio information"""
        return {
            'current_capital': self.capital,
            'initial_capital': 1000,
            'total_pnl': self.capital - 1000,
            'roi_percentage': ((self.capital - 1000) / 1000 * 100),
            'trades_today': self.trades_today,
            'consecutive_losses': self.consecutive_losses,
            'daily_loss': self.daily_loss,
            'max_risk_per_trade': self.max_risk_per_trade * 100,
            'can_trade': self.can_trade()
        }

    def reset_portfolio(self):
        """Reset portfolio to initial amount"""
        self.capital = 1000
        self.daily_loss = 0
        self.consecutive_losses = 0
        self.trades_today = 0
        self.trade_history = []
        logging.info("Portfolio reset to $1000")
        return True
        
    def calculate_position_size(self, entry_price, stop_loss_price, confidence=0.5):
        """Calculate position size based on risk management rules"""
        risk_amount = self.capital * self.max_risk_per_trade
        stop_percent = abs(entry_price - stop_loss_price) / entry_price
        
        if stop_percent == 0:
            stop_percent = 0.01
        
        position_size = risk_amount / stop_percent
        position_size = position_size * confidence
        
        if self.consecutive_losses >= 2:
            position_size *= 0.5
        if self.consecutive_losses >= 4:
            position_size *= 0.25
            
        max_position = self.capital * 0.25
        position_size = min(position_size, max_position)
        
        return position_size
    
    def update_after_trade(self, profit_loss):
        """Update risk metrics after a trade"""
        self.trade_history.append(profit_loss)
        self.trades_today += 1
        
        if profit_loss < 0:
            self.consecutive_losses += 1
            self.daily_loss += abs(profit_loss)
        else:
            self.consecutive_losses = 0
            
        self.capital += profit_loss
        return self.capital
    
    def can_trade(self):
        """Check if we can take new trades based on risk limits"""
        if self.daily_loss > self.capital * self.max_daily_risk:
            logging.warning(f"Daily loss limit reached: ${self.daily_loss:.2f}")
            return False
        if self.consecutive_losses >= 6:
            logging.warning("Too many consecutive losses, pausing trading")
            return False
        return True

# ===================== ADVANCED INDICATORS =====================
def calculate_atr(df, period=14):
    """Calculate Average True Range"""
    high = df['high']
    low = df['low']
    close = df['close']
    
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    
    return atr

def calculate_adx(df, period=14):
    """Calculate ADX for trend strength"""
    high = df['high']
    low = df['low']
    
    plus_dm = high.diff()
    minus_dm = low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0
    
    tr = calculate_atr(df, period)
    plus_di = 100 * (plus_dm.ewm(alpha=1/period).mean() / tr)
    minus_di = abs(100 * (minus_dm.ewm(alpha=1/period).mean() / tr))
    
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    adx = dx.ewm(alpha=1/period).mean()
    
    return adx

def add_advanced_indicators(df):
    """Add advanced technical indicators"""
    df = df.copy()
    
    df['atr'] = calculate_atr(df, 14)
    df['adx'] = calculate_adx(df, 14)
    df['vwap'] = (df['volume'] * df['close']).cumsum() / df['volume'].cumsum()
    df['volume_sma'] = df['volume'].rolling(20).mean()
    df['volume_ratio'] = df['volume'] / df['volume_sma']
    df['volatility'] = df['close'].pct_change().rolling(20).std()
    df['upper_wick'] = df['high'] - df[['open', 'close']].max(axis=1)
    df['lower_wick'] = df[['open', 'close']].min(axis=1) - df['low']
    df['body_size'] = abs(df['close'] - df['open'])
    df['trend_strength'] = abs(df['close'].rolling(20).mean() - df['close'].rolling(50).mean()) / df['close']
    df['is_ranging'] = (df['adx'] < 25).astype(int)
    df['resistance'] = df['high'].rolling(20).max()
    df['support'] = df['low'].rolling(20).min()
    df['dist_to_resistance'] = (df['resistance'] - df['close']) / df['close'] * 100
    df['dist_to_support'] = (df['close'] - df['support']) / df['close'] * 100
    
    return df

# ===================== MAIN PREDICTOR CLASS =====================
class BTCPredictorPro:

    def __init__(self):
        self.interval = "1h"
        self.df = None
        self.models = None
        self.scaler = StandardScaler()
        self.last_prediction = None
        self.last_signal = None
        self.last_update = None
        self.risk_manager = RiskManager(1000)
        self.trade_open = False
        self.entry_price = 0
        self.highest_price = 0
        self.stop_loss = 0
        self.take_profit = 0
        self.cache = {}
        
    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    def banner(self):
        self.clear()
        print(WHITE + BANNER + RESET)
        print(WHITE + "BTC Dump Pro v3.0 - Enhanced Edition" + RESET)
        print(WHITE + "Engine: XGBoost + RandomForest + GradientBoosting + Risk Management" + RESET)
        print(
            WHITE + f"Last Update: {self.last_update or 'Never'} | Interval: {self.interval} | Capital: ${self.risk_manager.capital:.2f}" + RESET)
        print(WHITE + "-" * 60 + RESET)

    @lru_cache(maxsize=32)
    def fetch_data(self, interval="1h", limit=1000):  
        cache_key = f"{interval}_{limit}"
        
        if cache_key in self.cache:
            cache_time, cache_data = self.cache[cache_key]
            if time.time() - cache_time < 300:
                logging.info(f"Using cached data for {interval}")
                return cache_data
        
        try:  
            params = {  
                "symbol": "BTCUSDT",  
                "interval": interval,  
                "limit": limit  
            }  

            headers = {"User-Agent": "Mozilla/5.0"}  

            response = requests.get(BINANCE_API, params=params, headers=headers, timeout=10)  

            if response.status_code != 200:  
                logging.error(f"API Error: {response.status_code}")
                return None  

            data = response.json()  

            df = pd.DataFrame(data, columns=[  
                "time", "open", "high", "low", "close", "volume",  
                "ct", "qav", "trades", "tb_base", "tb_quote", "ignore"  
            ])  

            numeric_cols = ["open", "high", "low", "close", "volume"]  

            for col in numeric_cols:  
                df[col] = pd.to_numeric(df[col], errors="coerce")  

            df["time"] = pd.to_datetime(df["time"], unit="ms")  
            df = df.sort_values("time").reset_index(drop=True)  

            self.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  
            self.cache[cache_key] = (time.time(), df)
            
            logging.info(f"Fetched {len(df)} candles for {interval}")
            return df  

        except requests.exceptions.RequestException as e:  
            logging.error(f"Network Error: {e}")
            return None  

    def indicators(self, df):  
        df = df.copy()  

        df["ma5"] = df["close"].rolling(5).mean()  
        df["ma20"] = df["close"].rolling(20).mean()  
        df["ma50"] = df["close"].rolling(50).mean()  
        df["ma200"] = df["close"].rolling(200).mean()

        delta = df["close"].diff()  
        gain = delta.where(delta > 0, 0).rolling(14).mean()  
        loss = -delta.where(delta < 0, 0).rolling(14).mean()  

        rs = gain / loss  
        df["RSI"] = 100 - (100 / (1 + rs))  

        exp1 = df["close"].ewm(span=12, adjust=False).mean()  
        exp2 = df["close"].ewm(span=26, adjust=False).mean()  

        df["MACD"] = exp1 - exp2  
        df["MACD_signal"] = df["MACD"].ewm(span=9, adjust=False).mean()  
        df["MACD_histogram"] = df["MACD"] - df["MACD_signal"]

        df["BB_middle"] = df["close"].rolling(20).mean()  
        bb_std = df["close"].rolling(20).std()  

        df["BB_upper"] = df["BB_middle"] + (bb_std * 2)  
        df["BB_lower"] = df["BB_middle"] - (bb_std * 2)  
        df["BB_width"] = (df["BB_upper"] - df["BB_lower"]) / df["BB_middle"]

        df["volume_sma"] = df["volume"].rolling(20).mean()  
        df["volume_ratio"] = df["volume"] / df["volume_sma"]  
        
        df = add_advanced_indicators(df)
        df = df.dropna()  
        return df  

    def features(self, df):  
        feature_cols = [  
            "close", "volume", "RSI", "MACD", "MACD_histogram",
            "volume_ratio", "ma5", "ma20", "ma50", "ma200",
            "BB_upper", "BB_lower", "BB_width", "atr", "adx",
            "volatility", "trend_strength"
        ]  

        X = []  
        y = []  
        window_size = 30

        for i in range(window_size, len(df) - 1):  
            window = df[feature_cols].iloc[i-window_size:i].values.flatten()  
            X.append(window)  
            y.append(df["close"].iloc[i+1])  

        return np.array(X), np.array(y)  

    def train(self, X, y):  
        split = int(len(X) * 0.85)  

        X_train, X_test = X[:split], X[split:]  
        y_train, y_test = y[:split], y[split:]  

        X_train_scaled = self.scaler.fit_transform(X_train)  
        X_test_scaled = self.scaler.transform(X_test)  

        xgb = XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=6, subsample=0.8, random_state=42, n_jobs=-1)
        rf = RandomForestRegressor(n_estimators=200, max_depth=10, min_samples_split=5, random_state=42, n_jobs=-1)
        gb = GradientBoostingRegressor(n_estimators=200, learning_rate=0.05, max_depth=5, random_state=42)

        logging.info("Training XGBoost...")
        xgb.fit(X_train_scaled, y_train)
        logging.info("Training Random Forest...")
        rf.fit(X_train_scaled, y_train)
        logging.info("Training Gradient Boosting...")
        gb.fit(X_train_scaled, y_train)  

        pred_xgb = xgb.predict(X_test_scaled)  
        pred_rf = rf.predict(X_test_scaled)  
        pred_gb = gb.predict(X_test_scaled)  

        errors = [
            mean_absolute_percentage_error(y_test, pred_xgb),
            mean_absolute_percentage_error(y_test, pred_rf),
            mean_absolute_percentage_error(y_test, pred_gb)
        ]
        
        weights = [1/e for e in errors]
        weights = [w/sum(weights) for w in weights]
        
        ensemble_pred = weights[0]*pred_xgb + weights[1]*pred_rf + weights[2]*pred_gb
        error = mean_absolute_percentage_error(y_test, ensemble_pred)
        
        logging.info(f"Model trained with error: {error:.4f}")
        logging.info(f"Model weights: XGB={weights[0]:.2f}, RF={weights[1]:.2f}, GB={weights[2]:.2f}")

        return {"xgb": xgb, "rf": rf, "gb": gb, "weights": weights, "error": error}

    def predict(self, models, features):  
        features_scaled = self.scaler.transform(features.reshape(1, -1))  
        p1 = models["xgb"].predict(features_scaled)[0]  
        p2 = models["rf"].predict(features_scaled)[0]  
        p3 = models["gb"].predict(features_scaled)[0]  
        weights = models.get("weights", [0.34, 0.33, 0.33])
        return weights[0]*p1 + weights[1]*p2 + weights[2]*p3

    def generate_signal(self, current_price, prediction, rsi, macd, macd_signal, adx, volume_ratio):
        """Generate signal with confidence score"""
        change_pct = ((prediction - current_price) / current_price) * 100
        confidence = 50
        
        if abs(change_pct) > 2:
            confidence += 20
        elif abs(change_pct) > 1:
            confidence += 10
            
        if change_pct > 0 and rsi < 70:
            confidence += 15
        elif change_pct < 0 and rsi > 30:
            confidence += 15
            
        if change_pct > 0 and macd > macd_signal:
            confidence += 15
        elif change_pct < 0 and macd < macd_signal:
            confidence += 15
            
        if volume_ratio > 1.5:
            confidence += 10
            
        if change_pct > 1.5 and confidence > 60:
            return "STRONG BUY", min(confidence, 100)
        elif change_pct > 0.5 and confidence > 50:
            return "BUY", min(confidence, 100)
        elif change_pct < -1.5 and confidence > 60:
            return "STRONG SELL", min(confidence, 100)
        elif change_pct < -0.5 and confidence > 50:
            return "SELL", min(confidence, 100)
        else:
            return "HOLD", confidence

    def manage_trade(self, current_price, signal):
        if not self.trade_open and signal in ["BUY", "STRONG BUY"]:
            confidence = 0.7 if signal == "STRONG BUY" else 0.5
            stop_loss_price = current_price * 0.98
            take_profit_price = current_price * 1.04
            
            position_size = self.risk_manager.calculate_position_size(current_price, stop_loss_price, confidence)
            
            if position_size > 0 and self.risk_manager.can_trade():
                self.trade_open = True
                self.entry_price = current_price
                self.stop_loss = stop_loss_price
                self.take_profit = take_profit_price
                self.highest_price = current_price
                logging.info(f"🟢 OPEN TRADE: Entry=${current_price:.2f}, SL=${stop_loss_price:.2f}, TP=${take_profit_price:.2f}")
                return True
                
        elif self.trade_open:
            if current_price > self.highest_price:
                self.highest_price = current_price
                new_stop = self.highest_price * 0.985
                if new_stop > self.stop_loss:
                    self.stop_loss = new_stop
                    logging.info(f"📈 Trailing stop updated to ${self.stop_loss:.2f}")
            
            if current_price <= self.stop_loss:
                pnl = current_price - self.entry_price
                self.risk_manager.update_after_trade(pnl)
                logging.info(f"🔴 STOP LOSS: Exit=${current_price:.2f}, P&L=${pnl:.2f}")
                self.trade_open = False
                return False
            elif current_price >= self.take_profit:
                pnl = current_price - self.entry_price
                self.risk_manager.update_after_trade(pnl)
                logging.info(f"🟢 TAKE PROFIT: Exit=${current_price:.2f}, P&L=${pnl:.2f}")
                self.trade_open = False
                return False
            elif signal in ["SELL", "STRONG SELL"]:
                pnl = current_price - self.entry_price
                self.risk_manager.update_after_trade(pnl)
                logging.info(f"⚠️ EARLY EXIT: Exit=${current_price:.2f}, P&L=${pnl:.2f}")
                self.trade_open = False
                return False
        return None

    def backtest(self, X, df):
        balance = 10
        position = 0
        entry_price = 0
        trades = 0
        winning_trades = 0
        
        for i in range(len(X)):
            if i + 30 >= len(df):
                break
                
            pred = self.predict(self.models, X[i])
            current_price = df["close"].iloc[i + 30]
            rsi = df["RSI"].iloc[i + 30]
            macd = df["MACD"].iloc[i + 30]
            macd_signal = df["MACD_signal"].iloc[i + 30]
            adx = df["adx"].iloc[i + 30] if "adx" in df.columns else 25
            volume_ratio = df["volume_ratio"].iloc[i + 30]
            
            signal, confidence = self.generate_signal(current_price, pred, rsi, macd, macd_signal, adx, volume_ratio)
            
            if position == 0 and signal in ["BUY", "STRONG BUY"]:
                position = 1
                entry_price = current_price
                stop_loss = current_price * 0.98
                take_profit = current_price * 1.04
                highest_price = current_price
                trades += 1
            elif position == 1:
                if current_price > highest_price:
                    highest_price = current_price
                    stop_loss = max(stop_loss, highest_price * 0.985)
                
                if current_price <= stop_loss:
                    pnl = current_price - entry_price
                    balance += pnl
                    position = 0
                    if pnl > 0:
                        winning_trades += 1
                elif current_price >= take_profit:
                    pnl = current_price - entry_price
                    balance += pnl
                    position = 0
                    if pnl > 0:
                        winning_trades += 1
                elif signal in ["SELL", "STRONG SELL"]:
                    pnl = current_price - entry_price
                    balance += pnl
                    position = 0
                    if pnl > 0:
                        winning_trades += 1
        
        if position == 1:
            balance += df["close"].iloc[-1] - entry_price
            
        win_rate = (winning_trades / trades * 100) if trades > 0 else 0
        return balance, trades, win_rate

    def chart(self):
        self.df = self.fetch_data(self.interval)
        if self.df is None or len(self.df) < 50:
            print("Failed to load chart data")
            return

        self.df = self.indicators(self.df)
        plt.style.use("dark_background")

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(4, 1, figsize=(14, 12))
        
        ax1.plot(self.df["time"], self.df["close"], label="BTC Price", linewidth=2, color='cyan')
        ax1.plot(self.df["time"], self.df["ma20"], label="MA20", linewidth=1, color='yellow')
        ax1.plot(self.df["time"], self.df["ma50"], label="MA50", linewidth=1, color='orange', alpha=0.7)
        ax1.fill_between(self.df["time"], self.df["BB_lower"], self.df["BB_upper"], alpha=0.1, color='gray')
        
        if self.last_prediction is not None:
            ax1.scatter(self.df["time"].iloc[-1], self.last_prediction, s=120, color='red', zorder=5)
            
        ax1.legend(loc='upper left')
        ax1.set_title(f'BTC Price - {self.interval} Timeframe', fontsize=14)
        ax1.set_ylabel('Price (USDT)')
        ax1.grid(True, alpha=0.3)
        
        ax2.plot(self.df["time"], self.df["RSI"], label="RSI", color='purple')
        ax2.axhline(70, linestyle="--", color='red', alpha=0.5)
        ax2.axhline(30, linestyle="--", color='green', alpha=0.5)
        ax2.fill_between(self.df["time"], 30, 70, alpha=0.1, color='gray')
        ax2.set_ylabel('RSI')
        ax2.grid(True, alpha=0.3)
        
        ax3.plot(self.df["time"], self.df["MACD"], label="MACD", color='blue')
        ax3.plot(self.df["time"], self.df["MACD_signal"], label="Signal", color='red')
        ax3.bar(self.df["time"], self.df["MACD_histogram"], label="Histogram", alpha=0.3)
        ax3.set_ylabel('MACD')
        ax3.legend(loc='upper left')
        ax3.grid(True, alpha=0.3)
        
        colors = ['g' if close >= open else 'r' for close, open in zip(self.df['close'], self.df['open'])]
        ax4.bar(self.df["time"], self.df["volume"], color=colors, alpha=0.6)
        ax4.plot(self.df["time"], self.df["volume_sma"], label="Volume SMA", color='yellow', linewidth=1)
        ax4.set_ylabel('Volume')
        ax4.set_xlabel('Time')
        ax4.legend(loc='upper left')
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()
        plt.close()

    def auto_live(self, delay=60):
        while True:
            try:
                self.banner()
                print("\n🤖 Auto Live Mode Running with Risk Management")
                print("-" * 50)

                self.df = self.fetch_data(self.interval)

                if self.df is None or len(self.df) < 100:
                    print("⚠️ Data error, retrying...")
                    time.sleep(delay)
                    continue

                self.df = self.indicators(self.df)
                X, y = self.features(self.df)
                self.models = self.train(X, y)

                last_features = X[-1]
                self.last_prediction = self.predict(self.models, last_features)

                current_price = self.df["close"].iloc[-1]
                rsi = self.df["RSI"].iloc[-1]
                macd = self.df["MACD"].iloc[-1]
                macd_signal = self.df["MACD_signal"].iloc[-1]
                adx = self.df["adx"].iloc[-1]
                volume_ratio = self.df["volume_ratio"].iloc[-1]

                self.last_signal, confidence = self.generate_signal(
                    current_price, self.last_prediction, rsi, macd, macd_signal, adx, volume_ratio
                )
                
                self.manage_trade(current_price, self.last_signal)
                change_pct = ((self.last_prediction - current_price) / current_price) * 100

                print(f"⏰ Time       : {datetime.now().strftime('%H:%M:%S')}")
                print(f"💰 Price      : ${current_price:,.2f}")
                print(f"🔮 Prediction : ${self.last_prediction:,.2f}")
                print(f"📈 Change     : {change_pct:+.2f}%")
                print(f"🎯 Signal     : {self.last_signal}")
                print(f"📊 Confidence : {confidence:.1f}%")
                print(f"📉 RSI        : {rsi:.1f}")
                print(f"📊 ADX        : {adx:.1f}")
                
                if self.trade_open:
                    print(f"💼 Trade Open : Entry=${self.entry_price:.2f}, SL=${self.stop_loss:.2f}, TP=${self.take_profit:.2f}")
                    
                print(f"💰 Capital    : ${self.risk_manager.capital:.2f}")
                print(f"🎯 Model Error: {self.models['error']*100:.2f}%")
                print("-" * 50)
                print(f"🔄 Next update in {delay} seconds... (Press Ctrl+C to stop)")

                time.sleep(delay)

            except KeyboardInterrupt:
                print("\n🛑 Stopped Auto Live Mode")
                break
            except Exception as e:
                logging.error(f"Error in auto_live: {e}")
                time.sleep(delay)

    # ===================== PORTFOLIO MANAGEMENT METHODS =====================
    def set_portfolio_amount(self, new_amount):
        """Change portfolio amount dynamically"""
        return self.risk_manager.set_portfolio_amount(new_amount)

    def get_portfolio_info(self):
        """Get detailed portfolio information"""
        return self.risk_manager.get_portfolio_info()

    def reset_portfolio(self):
        """Reset portfolio to initial amount"""
        return self.risk_manager.reset_portfolio()

    def main_menu(self):  
        while True:  
            self.banner()  

            print("1. 📊 Select Timeframe")  
            print("2. 🧠 Train & Predict")  
            print("3. 📈 Show Live Chart")  
            print("4. 🔄 Refresh Data Only")  
            print("5. 📋 Show Last Prediction")
            print("6. 🤖 Auto Live Mode (with Risk Management)") 
            print("7. 📉 Run Backtest")
            print("8. 💰 Show Portfolio Status")
            print("0. 🚪 Exit")  

            choice = input("\n👉 Choice: ").strip()  

            if choice == "0":
                print("\n👋 Goodbye! Happy Trading! 🚀")  
                break  

            elif choice == "1":
                print("\n📅 Available Timeframes:")
                for k, v in TIMEFRAMES.items():
                    print(f"  {k}. {v[1]}")
                
                sel = input("\n⏱️ Select timeframe: ").strip()
                if sel in TIMEFRAMES:
                    self.interval = TIMEFRAMES[sel][0]
                    print(f"✅ Timeframe set to {TIMEFRAMES[sel][1]}")
                else:
                    print("❌ Invalid selection")
                input("\n⏎ Press Enter...") 

            elif choice == "2":
                print("\n🔄 Fetching fresh market data...")
                self.df = self.fetch_data(self.interval)
                
                if self.df is None or len(self.df) < 100:
                    print("❌ Insufficient data for training")
                    input("\n⏎ Press Enter...")
                    continue
                
                print("📊 Computing technical indicators...")
                self.df = self.indicators(self.df)
                
                print("🧠 Training ensemble models...")
                X, y = self.features(self.df)
                self.models = self.train(X, y)  

                last_features = X[-1]
                self.last_prediction = self.predict(self.models, last_features)
                current_price = self.df["close"].iloc[-1]
                change_pct = ((self.last_prediction - current_price) / current_price) * 100
                rsi = self.df["RSI"].iloc[-1]
                macd = self.df["MACD"].iloc[-1]
                macd_signal = self.df["MACD_signal"].iloc[-1]
                adx = self.df["adx"].iloc[-1]
                volume_ratio = self.df["volume_ratio"].iloc[-1]
                
                self.last_signal, confidence = self.generate_signal(
                    current_price, self.last_prediction, rsi, macd, 
                    macd_signal, adx, volume_ratio
                )
                
                print("\n" + "="*70)
                print("📊 BTC ANALYSIS REPORT")
                print("="*70)
                print(f"💰 Current Price:  ${current_price:,.2f}")
                print(f"🔮 AI Prediction:  ${self.last_prediction:,.2f}")
                print(f"📈 Change:         {change_pct:+.2f}%")
                print(f"📉 RSI:            {rsi:.1f}")
                print(f"📊 ADX:            {adx:.1f}")
                print(f"🎯 Signal:         {self.last_signal}")
                print(f"📊 Confidence:     {confidence:.1f}%")
                print(f"⚡ Model Error:    {self.models['error']*100:.2f}%")
                print(f"⏱️ Timeframe:      {self.interval}")
                print(f"🕐 Last Update:    {self.last_update}")
                print("="*70)
                
                input("\n⏎ Press Enter to continue...")  

            elif choice == "3":
                self.chart()

            elif choice == "4":
                print("\n🔄 Refreshing data...")
                self.df = self.fetch_data(self.interval)
                if self.df is not None:
                    self.df = self.indicators(self.df)
                    print("✅ Data refreshed successfully!")
                input("\n⏎ Press Enter...")  

            elif choice == "5":
                if self.last_prediction:
                    print(f"\n📋 Last Analysis:")
                    print(f"🔮 Prediction: ${self.last_prediction:.2f}")
                    print(f"🎯 Signal: {self.last_signal}")
                else:
                    print("❌ No previous analysis. Run option 2 first.")
                input("\n⏎ Press Enter...")
         
            elif choice == "6":
                try:
                    delay = int(input("\n⏱️ Enter refresh time (seconds, min 30): ").strip())
                    if delay < 30:
                        delay = 30
                        print("⏰ Minimum delay set to 30 seconds")
                except:
                    delay = 60
                    print("⏰ Using default delay of 60 seconds")

                self.auto_live(delay)
                
            elif choice == "7":
                print("\n📊 Running backtest with risk management...")

                self.df = self.fetch_data(self.interval)
                self.df = self.indicators(self.df)

                X, y = self.features(self.df)
                self.models = self.train(X, y)

                final_balance, total_trades, win_rate = self.backtest(X, self.df)

                profit = final_balance - 1000
                roi = (profit / 1000) * 100

                print("\n" + "="*40)
                print("📊 BACKTEST RESULTS")
                print("="*40)
                print(f"💰 Initial Balance:  $1,000.00")
                print(f"💵 Final Balance:    ${final_balance:.2f}")
                print(f"📈 Profit/Loss:      ${profit:.2f}")
                print(f"📊 ROI:              {roi:+.2f}%")
                print(f"🔄 Total Trades:     {total_trades}")
                print(f"🏆 Win Rate:         {win_rate:.1f}%")
                print("="*40)

                input("\n⏎ Press Enter...")
                
            elif choice == "8":
                info = self.get_portfolio_info()
                print("\n" + "="*40)
                print("💰 PORTFOLIO STATUS")
                print("="*40)
                print(f"💵 Current Capital:  ${info['current_capital']:.2f}")
                print(f"📊 Initial Capital:  $1,000.00")
                print(f"📈 Total P&L:        ${info['total_pnl']:.2f}")
                print(f"📊 ROI:              {info['roi_percentage']:+.2f}%")
                print(f"🔄 Trades Today:     {info['trades_today']}")
                print(f"📉 Consecutive Losses: {info['consecutive_losses']}")
                print(f"⚠️ Max Risk/Trade:    {info['max_risk_per_trade']}%")
                print(f"🎯 Trading Status:    {'✅ Active' if info['can_trade'] else '⛔ Paused'}")
                
                if self.trade_open:
                    print(f"\n💼 OPEN TRADE:")
                    print(f"   Entry: ${self.entry_price:.2f}")
                    print(f"   Stop Loss: ${self.stop_loss:.2f}")
                    print(f"   Take Profit: ${self.take_profit:.2f}")
                print("="*40)
                
                # Option to change portfolio amount
                change = input("\n💰 Change portfolio amount? (y/n): ").strip().lower()
                if change == 'y':
                    try:
                        new_amount = float(input("Enter new amount (min $100): "))
                        if new_amount >= 100:
                            self.set_portfolio_amount(new_amount)
                            print(f"✅ Portfolio updated to ${new_amount:,.2f}")
                        else:
                            print("❌ Amount must be at least $100")
                    except:
                        print("❌ Invalid amount")
                
                input("\n⏎ Press Enter...")


def main():
    app = BTCPredictorPro()
    app.main_menu()

if __name__ == "__main__":
    main()