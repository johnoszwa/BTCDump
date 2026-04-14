# app.py - Complete Web UI with ALL Original Options
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

app = Flask(__name__)
CORS(app)

# Initialize predictor
predictor = BTCPredictorPro()

# HTML Template with ALL Original Options
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTC Dump Pro - Complete Trading Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
        
        .menu-card:active {
            transform: translateY(0);
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
        
        button, .btn {
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
        
        button:hover, .btn:hover {
            transform: scale(1.05);
        }
        
        button:active, .btn:active {
            transform: scale(0.95);
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
        
        input {
            cursor: text;
            width: 150px;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            display: none;
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
        
        .trade-log {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .trade-entry {
            padding: 10px;
            border-bottom: 1px solid #e5e7eb;
            font-size: 14px;
        }
        
        .trade-entry:hover {
            background: #f9fafb;
        }
        
        .portfolio-controls {
            display: flex;
            gap: 10px;
            align-items: center;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        
        .risk-meter {
            margin-top: 15px;
            padding: 10px;
            background: #f3f4f6;
            border-radius: 8px;
        }
        
        .risk-bar {
            height: 8px;
            background: #e5e7eb;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 5px;
        }
        
        .risk-fill {
            height: 100%;
            background: linear-gradient(90deg, #10b981, #f59e0b, #ef4444);
            transition: width 0.3s;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        
        .modal-content {
            background: white;
            padding: 30px;
            border-radius: 15px;
            max-width: 500px;
            width: 90%;
        }
        
        .modal-content input, .modal-content select {
            width: 100%;
            margin: 10px 0;
        }
        
        .info-panel {
            background: #f0fdf4;
            border-left: 4px solid #10b981;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 8px;
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
            <div class="info-panel" style="margin-top: 15px;">
                <strong>📋 Quick Guide:</strong> Click any menu button below → Train model first → Then use Auto Live or manual prediction
            </div>
        </div>
        
        <!-- Menu Grid - ALL Original Options -->
        <div class="menu-grid">
            <div class="menu-card" onclick="showTimeframeModal()">
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
            <div class="menu-card" onclick="showPortfolioModal()">
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
            <button onclick="quickPredict()">🔮 Quick Predict</button>
            <button onclick="startAutoUpdate()">🤖 Auto Refresh (30s)</button>
            <button onclick="stopAutoUpdate()">⏹️ Stop Refresh</button>
        </div>
        
        <!-- Stats Dashboard -->
        <div class="stats-grid" id="statsGrid">
            <!-- Stats will be loaded here -->
        </div>
        
        <!-- Chart -->
        <div class="chart-container">
            <div id="priceChart" style="height: 500px;"></div>
        </div>
        
        <!-- Additional Info -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Technical Indicators</div>
                <div id="indicators">
                    <!-- Indicators will be loaded here -->
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Model Performance</div>
                <div id="modelStats">
                    <!-- Model stats will be loaded here -->
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Trade Log</div>
                <div id="tradeLog" class="trade-log">
                    <!-- Trade log will be loaded here -->
                </div>
            </div>
        </div>
    </div>
    
    <!-- Timeframe Modal -->
    <div id="timeframeModal" class="modal">
        <div class="modal-content">
            <h2 style="margin-bottom: 20px;">📊 Select Timeframe</h2>
            <select id="modalTimeframe">
                <option value="1">5 Minutes</option>
                <option value="2">30 Minutes</option>
                <option value="3" selected>1 Hour</option>
                <option value="4">4 Hours</option>
                <option value="5">1 Day</option>
            </select>
            <div style="display: flex; gap: 10px; margin-top: 20px;">
                <button onclick="setTimeframe()" class="success">Apply</button>
                <button onclick="closeModal('timeframeModal')">Cancel</button>
            </div>
        </div>
    </div>
    
    <!-- Portfolio Modal -->
    <div id="portfolioModal" class="modal">
        <div class="modal-content">
            <h2 style="margin-bottom: 20px;">💰 Portfolio Management</h2>
            <label>Current Portfolio: $<span id="currentPortfolioDisplay">0</span></label>
            <input type="number" id="newPortfolioAmount" placeholder="Enter new amount" step="100" min="100">
            <div style="display: flex; gap: 10px; margin-top: 20px;">
                <button onclick="updatePortfolio()" class="success">Update Portfolio</button>
                <button onclick="resetPortfolio()" class="danger">Reset to $1000</button>
                <button onclick="closeModal('portfolioModal')">Cancel</button>
            </div>
        </div>
    </div>
    
    <!-- Auto Live Modal -->
    <div id="autoLiveModal" class="modal">
        <div class="modal-content">
            <h2 style="margin-bottom: 20px;">🤖 Auto Live Mode Settings</h2>
            <label>Refresh Interval (seconds):</label>
            <input type="number" id="autoLiveDelay" value="60" min="30">
            <div style="display: flex; gap: 10px; margin-top: 20px;">
                <button onclick="startAutoLive()" class="success">Start</button>
                <button onclick="closeModal('autoLiveModal')">Cancel</button>
            </div>
        </div>
    </div>
    
    <!-- Backtest Results Modal -->
    <div id="backtestModal" class="modal">
        <div class="modal-content">
            <h2 style="margin-bottom: 20px;">📊 Backtest Results</h2>
            <div id="backtestResults"></div>
            <button onclick="closeModal('backtestModal')" style="margin-top: 20px;">Close</button>
        </div>
    </div>
    
    <div class="loading" id="loading">
        <div class="spinner"></div>
        <p style="margin-top: 10px;">Processing...</p>
    </div>
    
    <script>
        let autoUpdateInterval = null;
        let autoLiveActive = false;
        
        // ============ ALL ORIGINAL MENU FUNCTIONS ============
        
        function showTimeframeModal() {
            document.getElementById('timeframeModal').style.display = 'flex';
        }
        
        function setTimeframe() {
            const tf = document.getElementById('modalTimeframe').value;
            changeTimeframe(tf);
            closeModal('timeframeModal');
        }
        
        function quickChangeTimeframe() {
            const tf = document.getElementById('timeframe').value;
            changeTimeframe(tf);
        }
        
        async function changeTimeframe(tf) {
            showLoading();
            try {
                const response = await fetch(`/api/timeframe/${tf}`, { method: 'POST' });
                const data = await response.json();
                if (data.success) {
                    alert(`✅ Timeframe changed to ${data.timeframe}`);
                    fetchData();
                }
            } catch (error) {
                console.error('Error:', error);
            } finally {
                hideLoading();
            }
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
                    alert('❌ Failed to train model');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('❌ Error training model');
            } finally {
                hideLoading();
            }
        }
        
        function quickTrain() {
            trainModel();
        }
        
        async function quickPredict() {
            showLoading();
            try {
                const response = await fetch('/api/predict');
                const data = await response.json();
                if (data.success) {
                    alert(`🔮 Prediction Complete!\nCurrent: $${data.current_price.toLocaleString()}\nPrediction: $${data.prediction.toLocaleString()}\nSignal: ${data.signal}\nConfidence: ${data.confidence}%`);
                    fetchData();
                }
            } catch (error) {
                console.error('Error:', error);
            } finally {
                hideLoading();
            }
        }
        
        async function showLiveChart() {
            showLoading();
            try {
                const response = await fetch('/api/chart');
                const data = await response.json();
                if (data.image) {
                    // Open chart in new window
                    const win = window.open();
                    win.document.write(`<img src="data:image/png;base64,${data.image}" style="max-width:100%">`);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error generating chart');
            } finally {
                hideLoading();
            }
        }
        
        async function refreshData() {
            showLoading();
            try {
                const response = await fetch('/api/refresh');
                const data = await response.json();
                if (data.success) {
                    alert('✅ Data refreshed successfully!');
                    fetchData();
                }
            } catch (error) {
                console.error('Error:', error);
            } finally {
                hideLoading();
            }
        }
        
        function showLastPrediction() {
            const predCard = document.querySelector('.stat-card:nth-child(2) .stat-value');
            const signalCard = document.querySelector('.stat-card:nth-child(3) .signal-badge');
            if (predCard && signalCard) {
                alert(`📋 Last Analysis:\nPrediction: ${predCard.innerText}\nSignal: ${signalCard.innerText}`);
            } else {
                alert('No prediction available. Train the model first.');
            }
        }
        
        function startAutoLive() {
            const delay = document.getElementById('autoLiveDelay').value;
            closeModal('autoLiveModal');
            showLoading();
            fetch('/api/auto_live/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ delay: parseInt(delay) })
            }).then(() => {
                alert(`🤖 Auto Live Mode started (updates every ${delay} seconds)`);
                autoLiveActive = true;
                startAutoUpdate();
                hideLoading();
            }).catch(err => {
                console.error(err);
                hideLoading();
            });
        }
        
        async function runBacktest() {
            showLoading();
            try {
                const response = await fetch('/api/backtest');
                const data = await response.json();
                if (data.success) {
                    document.getElementById('backtestResults').innerHTML = `
                        <div style="margin: 10px 0;">
                            <strong>Initial Balance:</strong> $1,000.00<br>
                            <strong>Final Balance:</strong> $${data.final_balance.toLocaleString()}<br>
                            <strong>Profit/Loss:</strong> <span class="${data.profit >= 0 ? 'positive' : 'negative'}">$${data.profit.toLocaleString()}</span><br>
                            <strong>ROI:</strong> <span class="${data.roi >= 0 ? 'positive' : 'negative'}">${data.roi.toFixed(2)}%</span><br>
                            <strong>Total Trades:</strong> ${data.total_trades}<br>
                            <strong>Win Rate:</strong> ${data.win_rate.toFixed(1)}%
                        </div>
                    `;
                    document.getElementById('backtestModal').style.display = 'flex';
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error running backtest');
            } finally {
                hideLoading();
            }
        }
        
        function showPortfolioModal() {
            const portfolioValue = document.querySelector('.stat-card:last-child .stat-value')?.innerText.replace('$', '') || '1000';
            document.getElementById('currentPortfolioDisplay').innerText = portfolioValue;
            document.getElementById('portfolioModal').style.display = 'flex';
        }
        
        async function updatePortfolio() {
            const newAmount = parseFloat(document.getElementById('newPortfolioAmount').value);
            if (isNaN(newAmount) || newAmount < 100) {
                alert('Please enter a valid amount (minimum $100)');
                return;
            }
            
            showLoading();
            try {
                const response = await fetch('/api/portfolio', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ amount: newAmount })
                });
                const data = await response.json();
                if (data.success) {
                    alert(`✅ Portfolio updated to $${newAmount.toLocaleString()}`);
                    closeModal('portfolioModal');
                    fetchData();
                }
            } catch (error) {
                console.error('Error:', error);
            } finally {
                hideLoading();
            }
        }
        
        async function resetPortfolio() {
            if (confirm('⚠️ Are you sure you want to reset your portfolio to $1000?')) {
                showLoading();
                try {
                    const response = await fetch('/api/portfolio/reset', { method: 'POST' });
                    const data = await response.json();
                    if (data.success) {
                        alert('✅ Portfolio reset to $1000');
                        closeModal('portfolioModal');
                        fetchData();
                    }
                } catch (error) {
                    console.error('Error:', error);
                } finally {
                    hideLoading();
                }
            }
        }
        
        // ============ DATA FETCHING ============
        
        async function fetchData() {
            try {
                const response = await fetch('/api/data');
                const data = await response.json();
                updateDashboard(data);
            } catch (error) {
                console.error('Error:', error);
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
                    ${data.portfolio.can_trade ? '<div class="stat-change positive">✅ Trading Active</div>' : '<div class="stat-change negative">⛔ Trading Paused</div>'}
                </div>
            `;
            
            // Update indicators
            document.getElementById('indicators').innerHTML = `
                <div style="margin-bottom: 10px;">
                    <strong>RSI:</strong> ${data.rsi.toFixed(1)}<br>
                    <div style="background: #e5e7eb; height: 8px; border-radius: 4px; margin-top: 5px;">
                        <div style="background: ${data.rsi > 70 ? '#ef4444' : data.rsi < 30 ? '#10b981' : '#667eea'}; width: ${data.rsi}%; height: 8px; border-radius: 4px;"></div>
                    </div>
                </div>
                <div style="margin-bottom: 10px;">
                    <strong>MACD:</strong> ${data.macd.toFixed(4)}<br>
                    <strong>Signal:</strong> ${data.macd_signal.toFixed(4)}
                </div>
                <div style="margin-bottom: 10px;">
                    <strong>ADX:</strong> ${data.adx.toFixed(1)}<br>
                    <strong>Trend:</strong> ${data.adx > 25 ? '📈 Trending' : '📊 Ranging'}
                </div>
                <div>
                    <strong>Volume Ratio:</strong> ${data.volume_ratio.toFixed(2)}x
                </div>
                <div class="risk-meter">
                    <strong>⚠️ Risk Management</strong>
                    <div style="margin-top: 10px;">
                        <div>Daily Risk: $${data.portfolio.daily_loss.toFixed(2)} / $${(data.portfolio.current_capital * 0.06).toFixed(2)}</div>
                        <div class="risk-bar">
                            <div class="risk-fill" style="width: ${Math.min((data.portfolio.daily_loss / (data.portfolio.current_capital * 0.06) * 100), 100)}%"></div>
                        </div>
                    </div>
                    <div>Consecutive Losses: ${data.portfolio.consecutive_losses}</div>
                    <div>Max Risk/Trade: ${data.portfolio.max_risk_per_trade}%</div>
                </div>
            `;
            
            // Update model stats
            document.getElementById('modelStats').innerHTML = `
                <div style="margin-bottom: 10px;">
                    <strong>Model Error:</strong> ${(data.model_error * 100).toFixed(2)}%
                </div>
                <div style="margin-bottom: 10px;">
                    <strong>Last Update:</strong><br>
                    ${data.last_update}
                </div>
                <div>
                    <strong>Timeframe:</strong> ${data.timeframe}
                </div>
                <div style="margin-top: 10px;">
                    <strong>Total P&L:</strong>
                    <span class="${data.portfolio.total_pnl >= 0 ? 'positive' : 'negative'}">
                        ${data.portfolio.total_pnl >= 0 ? '+' : ''}$${data.portfolio.total_pnl.toFixed(2)}
                    </span>
                </div>
            `;
            
            // Update chart
            if (data.chart_data) {
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
                line: { color: '#667eea', width: 2 },
                fill: 'tozeroy',
                fillcolor: 'rgba(102, 126, 234, 0.1)'
            };
            
            const layout = {
                title: 'Bitcoin Price Chart',
                xaxis: { title: 'Time', showgrid: true, gridcolor: '#e5e7eb' },
                yaxis: { title: 'Price (USDT)', showgrid: true, gridcolor: '#e5e7eb' },
                hovermode: 'closest',
                plot_bgcolor: 'white',
                paper_bgcolor: 'white'
            };
            
            Plotly.newPlot('priceChart', [trace], layout);
        }
        
        // ============ AUTO UPDATE ============
        
        function startAutoUpdate() {
            if (autoUpdateInterval) clearInterval(autoUpdateInterval);
            autoUpdateInterval = setInterval(fetchData, 30000);
            alert('🔄 Auto-refresh started (every 30 seconds)');
        }
        
        function stopAutoUpdate() {
            if (autoUpdateInterval) {
                clearInterval(autoUpdateInterval);
                autoUpdateInterval = null;
                alert('⏹️ Auto-refresh stopped');
            }
        }
        
        // ============ UTILITIES ============
        
        function closeModal(modalId) {
            document.getElementById(modalId).style.display = 'none';
        }
        
        function showLoading() {
            document.getElementById('loading').style.display = 'block';
        }
        
        function hideLoading() {
            document.getElementById('loading').style.display = 'none';
        }
        
        // Close modals when clicking outside
        window.onclick = function(event) {
            if (event.target.classList.contains('modal')) {
                event.target.style.display = 'none';
            }
        }
        
        // Initial load
        fetchData();
    </script>
</body>
</html>
'''

# ============ API ROUTES FOR ALL ORIGINAL FEATURES ============

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/data')
def get_data():
    """Get current prediction data"""
    try:
        predictor.df = predictor.fetch_data(predictor.interval)
        if predictor.df is not None and len(predictor.df) > 0:
            predictor.df = predictor.indicators(predictor.df)
            
            current_price = predictor.df['close'].iloc[-1]
            rsi = predictor.df['RSI'].iloc[-1]
            macd = predictor.df['MACD'].iloc[-1]
            macd_signal = predictor.df['MACD_signal'].iloc[-1]
            adx = predictor.df['adx'].iloc[-1] if 'adx' in predictor.df.columns else 25
            volume_ratio = predictor.df['volume_ratio'].iloc[-1]
            
            if predictor.models:
                X, y = predictor.features(predictor.df)
                if len(X) > 0:
                    last_features = X[-1]
                    prediction = predictor.predict(predictor.models, last_features)
                    signal, confidence = predictor.generate_signal(
                        current_price, prediction, rsi, macd, macd_signal, adx, volume_ratio
                    )
                else:
                    prediction = current_price
                    signal = "HOLD"
                    confidence = 0
            else:
                prediction = current_price
                signal = "TRAIN FIRST"
                confidence = 0
            
            chart_data = {
                'timestamps': predictor.df['time'].dt.strftime('%Y-%m-%d %H:%M').tolist()[-100:],
                'prices': predictor.df['close'].tolist()[-100:]
            }
            
            portfolio_info = predictor.get_portfolio_info()
            
            return jsonify({
                'current_price': current_price,
                'prediction': prediction,
                'signal': signal,
                'confidence': confidence,
                'rsi': rsi,
                'macd': macd,
                'macd_signal': macd_signal,
                'adx': adx,
                'volume_ratio': volume_ratio,
                'model_error': predictor.models['error'] if predictor.models else 0,
                'last_update': predictor.last_update or 'Never',
                'timeframe': predictor.interval,
                'portfolio': portfolio_info,
                'change_percent': ((current_price - predictor.df['close'].iloc[-2]) / predictor.df['close'].iloc[-2] * 100) if len(predictor.df) > 1 else 0,
                'chart_data': chart_data
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/train', methods=['POST'])
def train_model():
    """Train the model"""
    try:
        predictor.df = predictor.fetch_data(predictor.interval)
        if predictor.df is not None:
            predictor.df = predictor.indicators(predictor.df)
            X, y = predictor.features(predictor.df)
            predictor.models = predictor.train(X, y)
            return jsonify({'success': True, 'error': predictor.models['error']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict')
def quick_predict():
    """Quick prediction"""
    try:
        predictor.df = predictor.fetch_data(predictor.interval)
        if predictor.df and predictor.models:
            predictor.df = predictor.indicators(predictor.df)
            X, y = predictor.features(predictor.df)
            if len(X) > 0:
                last_features = X[-1]
                prediction = predictor.predict(predictor.models, last_features)
                current_price = predictor.df['close'].iloc[-1]
                return jsonify({
                    'success': True,
                    'current_price': current_price,
                    'prediction': prediction,
                    'signal': "READY",
                    'confidence': 75
                })
        return jsonify({'success': False})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chart')
def get_chart():
    """Generate and return chart as image"""
    try:
        predictor.df = predictor.fetch_data(predictor.interval)
        if predictor.df is not None:
            predictor.df = predictor.indicators(predictor.df)
            
            # Create plot
            plt.style.use("dark_background")
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(predictor.df["time"], predictor.df["close"], label="BTC Price", linewidth=2, color='cyan')
            ax.plot(predictor.df["time"], predictor.df["ma20"], label="MA20", linewidth=1, color='yellow')
            ax.legend()
            ax.set_title(f'BTC Price - {predictor.interval}')
            ax.set_ylabel('Price (USDT)')
            ax.grid(True, alpha=0.3)
            
            # Convert to base64
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode()
            plt.close()
            
            return jsonify({'image': img_base64})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/refresh')
def refresh_data():
    """Refresh data only"""
    try:
        predictor.df = predictor.fetch_data(predictor.interval)
        if predictor.df is not None:
            predictor.df = predictor.indicators(predictor.df)
            return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/backtest')
def run_backtest():
    """Run backtest"""
    try:
        predictor.df = predictor.fetch_data(predictor.interval)
        if predictor.df is not None:
            predictor.df = predictor.indicators(predictor.df)
            X, y = predictor.features(predictor.df)
            predictor.models = predictor.train(X, y)
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
        return jsonify({'error': str(e)}), 500

@app.route('/api/auto_live/start', methods=['POST'])
def start_auto_live():
    """Start auto live mode in background"""
    data = request.json
    delay = data.get('delay', 60)
    
    def run_auto():
        predictor.auto_live(delay)
    
    thread = threading.Thread(target=run_auto, daemon=True)
    thread.start()
    return jsonify({'success': True})

@app.route('/api/timeframe/<tf>', methods=['POST'])
def change_timeframe(tf):
    """Change timeframe"""
    timeframe_map = {'1': '5m', '2': '30m', '3': '1h', '4': '4h', '5': '1d'}
    predictor.interval = timeframe_map.get(tf, '1h')
    return jsonify({'success': True, 'timeframe': predictor.interval})

@app.route('/api/portfolio', methods=['POST'])
def update_portfolio():
    """Update portfolio amount"""
    try:
        data = request.json
        new_amount = float(data.get('amount', 0))
        if predictor.set_portfolio_amount(new_amount):
            return jsonify({'success': True, 'new_amount': new_amount})
        return jsonify({'success': False}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/reset', methods=['POST'])
def reset_portfolio():
    """Reset portfolio"""
    try:
        predictor.reset_portfolio()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("="*60)
    print("🚀 BTC Dump Pro - Complete Trading Dashboard")
    print("="*60)
    print("\n📋 ALL ORIGINAL MENU OPTIONS AVAILABLE:")
    print("   1. Select Timeframe")
    print("   2. Train & Predict")
    print("   3. Show Live Chart")
    print("   4. Refresh Data Only")
    print("   5. Show Last Prediction")
    print("   6. Auto Live Mode")
    print("   7. Run Backtest")
    print("   8. Portfolio Status (NEW!)")
    print("\n💰 NEW: Dynamic Portfolio Management")
    print("   - Change portfolio amount anytime")
    print("   - Real-time risk tracking")
    print("   - Automatic position sizing")
    print("\n📊 Open your browser: http://localhost:5000")
    print("⚡ Press Ctrl+C to stop the server")
    print("="*60)
    app.run(debug=True, host='0.0.0.0', port=5000)