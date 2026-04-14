# app.py - Complete Web UI with ALL Original Options (Fixed Version)
from flask import Flask, render_template_string, jsonify, request, send_file
from flask_cors import CORS
import threading
import time
import pandas as pd
import numpy as np
from datetime import datetime
import json
import plotly.graph_objs as go
import plotly.utils
import io
import base64
import matplotlib.pyplot as plt
from BTCDump import BTCPredictorPro
import logging

app = Flask(__name__)
CORS(app)

# Initialize predictor
predictor = BTCPredictorPro()

# Configure logging
logging.basicConfig(level=logging.INFO)

# HTML Template with ALL Original Options
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTC Dump Pro - Complete Trading Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
        }
        
        .header {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .title {
            font-size: 32px;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .menu-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .menu-card {
            background: white;
            border-radius: 12px;
            padding: 15px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .menu-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .menu-icon {
            font-size: 32px;
            margin-bottom: 10px;
        }
        
        .menu-title {
            font-weight: bold;
            font-size: 14px;
            color: #333;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-label {
            font-size: 14px;
            color: #666;
            margin-bottom: 10px;
        }
        
        .stat-value {
            font-size: 28px;
            font-weight: bold;
            color: #333;
        }
        
        .stat-change {
            font-size: 14px;
            margin-top: 10px;
        }
        
        .positive {
            color: #10b981;
        }
        
        .negative {
            color: #ef4444;
        }
        
        .signal-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 18px;
        }
        
        .signal-STRONG_BUY { background: #10b981; color: white; }
        .signal-BUY { background: #34d399; color: white; }
        .signal-STRONG_SELL { background: #ef4444; color: white; }
        .signal-SELL { background: #f87171; color: white; }
        .signal-HOLD { background: #f59e0b; color: white; }
        
        .chart-container {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            transition: transform 0.2s;
        }
        
        button:hover {
            transform: scale(1.05);
        }
        
        button.danger {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        }
        
        button.success {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        }
        
        select, input {
            padding: 12px 24px;
            border-radius: 8px;
            border: 2px solid #e5e7eb;
            font-size: 14px;
            cursor: pointer;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0,0,0,0.8);
            border-radius: 10px;
            color: white;
            z-index: 1000;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .error-message {
            background: #fee2e2;
            border-left: 4px solid #ef4444;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 8px;
            color: #991b1b;
        }
        
        @media (max-width: 768px) {
            .stats-grid {
                grid-template-columns: 1fr;
            }
            .stat-value {
                font-size: 20px;
            }
            .controls {
                flex-direction: column;
            }
            button, select, input {
                width: 100%;
            }
            .menu-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="title">🚀 BTC Dump Pro - Complete Trading Dashboard</div>
            <div style="margin-top: 10px; color: #666;">All original features + Advanced Portfolio Management</div>
            <div id="connectionStatus" style="margin-top: 10px; padding: 8px; border-radius: 5px; background: #f3f4f6;">
                ⚠️ Checking connection to Binance API...
            </div>
        </div>
        
        <!-- Menu Grid - ALL Original Options -->
        <div class="menu-grid">
            <div class="menu-card" onclick="changeTimeframe()">
                <div class="menu-icon">📊</div>
                <div class="menu-title">1. Select Timeframe</div>
            </div>
            <div class="menu-card" onclick="trainModel()">
                <div class="menu-icon">🧠</div>
                <div class="menu-title">2. Train & Predict</div>
            </div>
            <div class="menu-card" onclick="showLiveChart()">
                <div class="menu-icon">📈</div>
                <div class="menu-title">3. Show Live Chart</div>
            </div>
            <div class="menu-card" onclick="refreshData()">
                <div class="menu-icon">🔄</div>
                <div class="menu-title">4. Refresh Data Only</div>
            </div>
            <div class="menu-card" onclick="showLastPrediction()">
                <div class="menu-icon">📋</div>
                <div class="menu-title">5. Show Last Prediction</div>
            </div>
            <div class="menu-card" onclick="startAutoLive()">
                <div class="menu-icon">🤖</div>
                <div class="menu-title">6. Auto Live Mode</div>
            </div>
            <div class="menu-card" onclick="runBacktest()">
                <div class="menu-icon">📉</div>
                <div class="menu-title">7. Run Backtest</div>
            </div>
            <div class="menu-card" onclick="showPortfolioStatus()">
                <div class="menu-icon">💰</div>
                <div class="menu-title">8. Portfolio Status</div>
            </div>
        </div>
        
        <!-- Quick Controls -->
        <div class="controls">
            <select id="timeframe" onchange="quickChangeTimeframe()">
                <option value="1">5 Minutes</option>
                <option value="2">30 Minutes</option>
                <option value="3" selected>1 Hour</option>
                <option value="4">4 Hours</option>
                <option value="5">1 Day</option>
            </select>
            <button onclick="quickTrain()" class="success">🚀 Quick Train</button>
            <button onclick="fetchData()">🔄 Refresh Dashboard</button>
        </div>
        
        <!-- Stats Dashboard -->
        <div class="stats-grid" id="statsGrid">
            <div class="stat-card">
                <div class="stat-label">💰 Current Price</div>
                <div class="stat-value">Loading...</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">🔮 AI Prediction</div>
                <div class="stat-value">Train model first</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">🎯 Signal</div>
                <div class="stat-value">N/A</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">💼 Portfolio</div>
                <div class="stat-value">$1,000</div>
            </div>
        </div>
        
        <!-- Chart -->
        <div class="chart-container">
            <div id="priceChart" style="height: 500px;">
                <p style="text-align: center; padding: 50px;">Loading chart... Please train the model first (Option 2)</p>
            </div>
        </div>
        
        <!-- Additional Info -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Technical Indicators</div>
                <div id="indicators">Waiting for data...</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Model Performance</div>
                <div id="modelStats">Not trained yet</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Trade Log</div>
                <div id="tradeLog" style="max-height: 300px; overflow-y: auto;">No trades yet</div>
            </div>
        </div>
    </div>
    
    <div class="loading" id="loading">
        <div class="spinner"></div>
        <p style="margin-top: 10px;">Processing...</p>
    </div>
    
    <script>
        let autoUpdateInterval = null;
        
        async function fetchData() {
            showLoading();
            try {
                const response = await fetch('/api/data');
                const data = await response.json();
                
                if (data.error) {
                    document.getElementById('connectionStatus').innerHTML = '❌ ' + data.error;
                    document.getElementById('connectionStatus').style.background = '#fee2e2';
                    return;
                }
                
                document.getElementById('connectionStatus').innerHTML = '✅ Connected to Binance API | Last Update: ' + data.last_update;
                document.getElementById('connectionStatus').style.background = '#d1fae5';
                
                updateDashboard(data);
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('connectionStatus').innerHTML = '❌ Connection error: ' + error.message;
                document.getElementById('connectionStatus').style.background = '#fee2e2';
            } finally {
                hideLoading();
            }
        }
        
        function updateDashboard(data) {
            // Update stats cards
            const statsGrid = document.getElementById('statsGrid');
            statsGrid.innerHTML = `
                <div class="stat-card">
                    <div class="stat-label">💰 Current Price</div>
                    <div class="stat-value">$${data.current_price.toLocaleString()}</div>
                    <div class="stat-change ${data.change_percent >= 0 ? 'positive' : 'negative'}">
                        ${data.change_percent >= 0 ? '▲' : '▼'} ${Math.abs(data.change_percent).toFixed(2)}%
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">🔮 AI Prediction</div>
                    <div class="stat-value">$${data.prediction.toLocaleString()}</div>
                    <div class="stat-change">Target: ${((data.prediction - data.current_price) / data.current_price * 100).toFixed(2)}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">🎯 Signal</div>
                    <div class="signal-badge signal-${data.signal.replace(' ', '_')}">${data.signal}</div>
                    <div class="stat-change">Confidence: ${data.confidence}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">💼 Portfolio Value</div>
                    <div class="stat-value">$${data.portfolio.current_capital.toLocaleString()}</div>
                    <div class="stat-change ${data.portfolio.roi_percentage >= 0 ? 'positive' : 'negative'}">
                        ROI: ${data.portfolio.roi_percentage >= 0 ? '+' : ''}${data.portfolio.roi_percentage.toFixed(2)}%
                    </div>
                </div>
            `;
            
            // Update indicators
            document.getElementById('indicators').innerHTML = `
                <div><strong>RSI:</strong> ${data.rsi.toFixed(1)}</div>
                <div><strong>MACD:</strong> ${data.macd.toFixed(4)}</div>
                <div><strong>ADX:</strong> ${data.adx.toFixed(1)}</div>
                <div><strong>Volume Ratio:</strong> ${data.volume_ratio.toFixed(2)}x</div>
                <div><strong>Model Error:</strong> ${(data.model_error * 100).toFixed(2)}%</div>
            `;
            
            // Update model stats
            document.getElementById('modelStats').innerHTML = `
                <div><strong>Timeframe:</strong> ${data.timeframe}</div>
                <div><strong>Last Update:</strong> ${data.last_update}</div>
                <div><strong>Total P&L:</strong> $${data.portfolio.total_pnl.toFixed(2)}</div>
                <div><strong>Trades Today:</strong> ${data.portfolio.trades_today}</div>
            `;
            
            // Update chart
            if (data.chart_data && data.chart_data.prices.length > 0) {
                updateChart(data.chart_data);
            }
        }
        
        function updateChart(chartData) {
            const trace = {
                x: chartData.timestamps,
                y: chartData.prices,
                type: 'scatter',
                mode: 'lines',
                name: 'BTC Price',
                line: { color: '#667eea', width: 2 }
            };
            
            const layout = {
                title: 'Bitcoin Price Chart',
                xaxis: { title: 'Time' },
                yaxis: { title: 'Price (USDT)' },
                hovermode: 'closest'
            };
            
            Plotly.newPlot('priceChart', [trace], layout);
        }
        
        async function trainModel() {
            showLoading();
            try {
                const response = await fetch('/api/train', { method: 'POST' });
                const data = await response.json();
                if (data.success) {
                    alert(`✅ Model trained successfully!\nError: ${(data.error * 100).toFixed(2)}%`);
                    fetchData();
                } else {
                    alert('❌ Failed to train model: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                alert('❌ Error training model: ' + error.message);
            } finally {
                hideLoading();
            }
        }
        
        async function quickTrain() {
            await trainModel();
        }
        
        async function changeTimeframe() {
            const tf = prompt('Enter timeframe:\n1=5min, 2=30min, 3=1h, 4=4h, 5=1d', '3');
            if (tf) {
                showLoading();
                try {
                    const response = await fetch(`/api/timeframe/${tf}`, { method: 'POST' });
                    const data = await response.json();
                    if (data.success) {
                        alert(`✅ Timeframe changed to ${data.timeframe}`);
                        fetchData();
                    }
                } catch (error) {
                    alert('Error changing timeframe');
                } finally {
                    hideLoading();
                }
            }
        }
        
        async function quickChangeTimeframe() {
            const tf = document.getElementById('timeframe').value;
            showLoading();
            try {
                const response = await fetch(`/api/timeframe/${tf}`, { method: 'POST' });
                const data = await response.json();
                if (data.success) {
                    fetchData();
                }
            } catch (error) {
                console.error('Error:', error);
            } finally {
                hideLoading();
            }
        }
        
        async function showLiveChart() {
            alert('Chart is displayed above. Train the model first (Option 2) to see predictions.');
        }
        
        async function refreshData() {
            await fetchData();
            alert('Data refreshed!');
        }
        
        function showLastPrediction() {
            fetch('/api/last_prediction')
                .then(res => res.json())
                .then(data => {
                    alert(`📋 Last Analysis:\nPrediction: $${data.prediction.toLocaleString()}\nSignal: ${data.signal}`);
                })
                .catch(() => alert('No prediction available. Train the model first.'));
        }
        
        async function startAutoLive() {
            const delay = prompt('Enter refresh interval (seconds, min 30):', '60');
            if (delay && delay >= 30) {
                showLoading();
                try {
                    await fetch('/api/auto_live/start', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ delay: parseInt(delay) })
                    });
                    alert(`🤖 Auto Live Mode started (updates every ${delay} seconds)`);
                    if (autoUpdateInterval) clearInterval(autoUpdateInterval);
                    autoUpdateInterval = setInterval(fetchData, delay * 1000);
                } catch (error) {
                    alert('Error starting auto mode');
                } finally {
                    hideLoading();
                }
            } else {
                alert('Please enter a valid delay (minimum 30 seconds)');
            }
        }
        
        async function runBacktest() {
            showLoading();
            try {
                const response = await fetch('/api/backtest');
                const data = await response.json();
                if (data.success) {
                    alert(`📊 Backtest Results:\nFinal Balance: $${data.final_balance.toLocaleString()}\nProfit: $${data.profit.toLocaleString()}\nROI: ${data.roi.toFixed(2)}%\nWin Rate: ${data.win_rate.toFixed(1)}%`);
                } else {
                    alert('Backtest failed. Train the model first.');
                }
            } catch (error) {
                alert('Error running backtest');
            } finally {
                hideLoading();
            }
        }
        
        async function showPortfolioStatus() {
            try {
                const response = await fetch('/api/portfolio');
                const data = await response.json();
                const change = prompt(`💰 Portfolio Status\n\nCurrent: $${data.current_capital.toLocaleString()}\nP&L: $${data.total_pnl.toLocaleString()}\nROI: ${data.roi_percentage.toFixed(2)}%\nTrades Today: ${data.trades_today}\n\nEnter new amount (min $100) or click Cancel:`, data.current_capital);
                if (change && parseFloat(change) >= 100) {
                    await updatePortfolio(parseFloat(change));
                } else if (change && parseFloat(change) < 100) {
                    alert('Minimum amount is $100');
                }
            } catch (error) {
                alert('Error fetching portfolio status');
            }
        }
        
        async function updatePortfolio(amount) {
            showLoading();
            try {
                const response = await fetch('/api/portfolio', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ amount: amount })
                });
                const data = await response.json();
                if (data.success) {
                    alert(`✅ Portfolio updated to $${amount.toLocaleString()}`);
                    fetchData();
                }
            } catch (error) {
                alert('Error updating portfolio');
            } finally {
                hideLoading();
            }
        }
        
        function showLoading() {
            document.getElementById('loading').style.display = 'block';
        }
        
        function hideLoading() {
            document.getElementById('loading').style.display = 'none';
        }
        
        // Initial load
        fetchData();
        
        // Auto refresh every 60 seconds
        setInterval(fetchData, 60000);
    </script>
</body>
</html>
'''

# ============ API ROUTES ============

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/data')
def get_data():
    """Get current prediction data"""
    try:
        # Try to fetch data
        df = predictor.fetch_data(predictor.interval)
        
        if df is None or len(df) == 0:
            return jsonify({
                'error': 'Unable to fetch data from Binance API. Please check your internet connection.',
                'current_price': 0,
                'prediction': 0,
                'signal': 'NO DATA',
                'confidence': 0,
                'rsi': 0,
                'macd': 0,
                'macd_signal': 0,
                'adx': 0,
                'volume_ratio': 0,
                'model_error': 0,
                'last_update': 'Never',
                'timeframe': predictor.interval,
                'portfolio': predictor.get_portfolio_info(),
                'change_percent': 0,
                'chart_data': {'timestamps': [], 'prices': []}
            })
        
        predictor.df = predictor.indicators(df)
        
        if predictor.df is None or len(predictor.df) == 0:
            return jsonify({'error': 'Error calculating indicators'})
        
        current_price = float(predictor.df['close'].iloc[-1])
        rsi = float(predictor.df['RSI'].iloc[-1]) if 'RSI' in predictor.df.columns else 50
        macd = float(predictor.df['MACD'].iloc[-1]) if 'MACD' in predictor.df.columns else 0
        macd_signal = float(predictor.df['MACD_signal'].iloc[-1]) if 'MACD_signal' in predictor.df.columns else 0
        adx = float(predictor.df['adx'].iloc[-1]) if 'adx' in predictor.df.columns else 25
        volume_ratio = float(predictor.df['volume_ratio'].iloc[-1]) if 'volume_ratio' in predictor.df.columns else 1
        
        # Make prediction if model exists
        if predictor.models:
            try:
                X, y = predictor.features(predictor.df)
                if len(X) > 0:
                    last_features = X[-1]
                    prediction = float(predictor.predict(predictor.models, last_features))
                    signal, confidence = predictor.generate_signal(
                        current_price, prediction, rsi, macd, macd_signal, adx, volume_ratio
                    )
                else:
                    prediction = current_price
                    signal = "HOLD"
                    confidence = 0
            except Exception as e:
                logging.error(f"Prediction error: {e}")
                prediction = current_price
                signal = "ERROR"
                confidence = 0
        else:
            prediction = current_price
            signal = "TRAIN FIRST"
            confidence = 0
        
        # Prepare chart data
        chart_data = {
            'timestamps': predictor.df['time'].dt.strftime('%Y-%m-%d %H:%M').tolist()[-100:],
            'prices': [float(x) for x in predictor.df['close'].tolist()[-100:]]
        }
        
        portfolio_info = predictor.get_portfolio_info()
        
        # Calculate change percentage
        change_percent = 0
        if len(predictor.df) > 1:
            prev_close = float(predictor.df['close'].iloc[-2])
            change_percent = ((current_price - prev_close) / prev_close * 100)
        
        return jsonify({
            'current_price': current_price,
            'prediction': prediction,
            'signal': signal,
            'confidence': int(confidence),
            'rsi': rsi,
            'macd': macd,
            'macd_signal': macd_signal,
            'adx': adx,
            'volume_ratio': volume_ratio,
            'model_error': float(predictor.models['error']) if predictor.models else 0,
            'last_update': predictor.last_update or 'Never',
            'timeframe': predictor.interval,
            'portfolio': portfolio_info,
            'change_percent': change_percent,
            'chart_data': chart_data
        })
        
    except Exception as e:
        logging.error(f"Error in get_data: {str(e)}")
        return jsonify({
            'error': str(e),
            'current_price': 0,
            'prediction': 0,
            'signal': 'ERROR',
            'confidence': 0,
            'rsi': 0,
            'macd': 0,
            'macd_signal': 0,
            'adx': 0,
            'volume_ratio': 0,
            'model_error': 0,
            'last_update': 'Never',
            'timeframe': predictor.interval,
            'portfolio': predictor.get_portfolio_info(),
            'change_percent': 0,
            'chart_data': {'timestamps': [], 'prices': []}
        })

@app.route('/api/train', methods=['POST'])
def train_model():
    """Train the model"""
    try:
        df = predictor.fetch_data(predictor.interval)
        if df is None or len(df) < 100:
            return jsonify({'success': False, 'error': 'Insufficient data. Need at least 100 candles.'})
        
        predictor.df = predictor.indicators(df)
        X, y = predictor.features(predictor.df)
        
        if len(X) == 0:
            return jsonify({'success': False, 'error': 'Not enough data for training.'})
        
        predictor.models = predictor.train(X, y)
        return jsonify({'success': True, 'error': predictor.models['error']})
        
    except Exception as e:
        logging.error(f"Training error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/timeframe/<tf>', methods=['POST'])
def change_timeframe(tf):
    """Change timeframe"""
    timeframe_map = {'1': '5m', '2': '30m', '3': '1h', '4': '4h', '5': '1d'}
    predictor.interval = timeframe_map.get(tf, '1h')
    return jsonify({'success': True, 'timeframe': predictor.interval})

@app.route('/api/backtest')
def run_backtest():
    """Run backtest"""
    try:
        if not predictor.models:
            return jsonify({'success': False, 'error': 'Please train the model first (Option 2)'})
        
        df = predictor.fetch_data(predictor.interval)
        if df is None:
            return jsonify({'success': False, 'error': 'Failed to fetch data'})
        
        predictor.df = predictor.indicators(df)
        X, y = predictor.features(predictor.df)
        
        final_balance, total_trades, win_rate = predictor.backtest(X, predictor.df)
        
        return jsonify({
            'success': True,
            'final_balance': final_balance,
            'profit': final_balance - 1000,
            'roi': ((final_balance - 1000) / 1000 * 100),
            'total_trades': total_trades,
            'win_rate': win_rate
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/portfolio', methods=['GET', 'POST'])
def handle_portfolio():
    """Get or update portfolio"""
    if request.method == 'GET':
        return jsonify(predictor.get_portfolio_info())
    else:
        try:
            data = request.json
            new_amount = float(data.get('amount', 0))
            if predictor.set_portfolio_amount(new_amount):
                return jsonify({'success': True, 'new_amount': new_amount})
            return jsonify({'success': False, 'error': 'Invalid amount'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

@app.route('/api/last_prediction')
def last_prediction():
    """Get last prediction"""
    return jsonify({
        'prediction': predictor.last_prediction or 0,
        'signal': predictor.last_signal or 'N/A'
    })

@app.route('/api/auto_live/start', methods=['POST'])
def start_auto_live():
    """Start auto live mode"""
    data = request.json
    delay = data.get('delay', 60)
    
    def run_auto():
        predictor.auto_live(delay)
    
    thread = threading.Thread(target=run_auto, daemon=True)
    thread.start()
    return jsonify({'success': True})

if __name__ == '__main__':
    print("="*60)
    print("🚀 BTC Dump Pro - Complete Trading Dashboard")
    print("="*60)
    print("\n📋 IMPORTANT - First Time Setup:")
    print("   1. Make sure you have an internet connection")
    print("   2. Click 'Quick Train' to train the AI model")
    print("   3. Wait 10-30 seconds for training to complete")
    print("   4. Dashboard will update automatically")
    print("\n📊 Open your browser: http://localhost:5000")
    print("⚡ Press Ctrl+C to stop the server")
    print("="*60)
    app.run(debug=True, host='0.0.0.0', port=5000)