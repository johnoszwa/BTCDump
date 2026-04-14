# app_offline.py - Works offline with demo data
from flask import Flask, render_template_string, jsonify, request
import random
import time
from datetime import datetime
import threading

app = Flask(__name__)

# Demo data generator
class DemoBTCData:
    def __init__(self):
        self.current_price = 50000
        self.trend = 0
        self.models = None
        self.interval = "1h"
        self.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.risk_manager = type('obj', (object,), {
            'capital': 1000,
            'trades_today': 0,
            'consecutive_losses': 0,
            'daily_loss': 0,
            'max_risk_per_trade': 2.0
        })()
        
    def fetch_data(self):
        # Generate realistic demo data
        self.trend += random.uniform(-0.02, 0.03)
        self.trend = max(-0.1, min(0.1, self.trend))
        change = self.trend + random.uniform(-0.01, 0.01)
        self.current_price *= (1 + change)
        self.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return True
        
    def get_indicators(self):
        return {
            'rsi': random.uniform(30, 70),
            'macd': random.uniform(-100, 100),
            'macd_signal': random.uniform(-100, 100),
            'adx': random.uniform(20, 40),
            'volume_ratio': random.uniform(0.5, 2.5)
        }
    
    def predict(self):
        # Simulate prediction
        change_percent = random.uniform(-3, 3)
        prediction = self.current_price * (1 + change_percent/100)
        return prediction
    
    def generate_signal(self, current, prediction, *args):
        change_pct = ((prediction - current) / current) * 100
        if change_pct > 1.5:
            return "STRONG BUY", random.uniform(70, 95)
        elif change_pct > 0.5:
            return "BUY", random.uniform(60, 80)
        elif change_pct < -1.5:
            return "STRONG SELL", random.uniform(70, 95)
        elif change_pct < -0.5:
            return "SELL", random.uniform(60, 80)
        else:
            return "HOLD", random.uniform(30, 60)
    
    def get_portfolio_info(self):
        return {
            'current_capital': self.risk_manager.capital,
            'initial_capital': 1000,
            'total_pnl': self.risk_manager.capital - 1000,
            'roi_percentage': ((self.risk_manager.capital - 1000) / 1000 * 100),
            'trades_today': self.risk_manager.trades_today,
            'consecutive_losses': self.risk_manager.consecutive_losses,
            'daily_loss': self.risk_manager.daily_loss,
            'max_risk_per_trade': self.risk_manager.max_risk_per_trade,
            'can_trade': True
        }
    
    def set_portfolio_amount(self, amount):
        if amount > 0:
            self.risk_manager.capital = amount
            return True
        return False

predictor = DemoBTCData()

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTC Dump Pro - Offline Demo Mode</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            padding: 20px;
            color: white;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .title {
            font-size: 32px;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .demo-badge {
            display: inline-block;
            background: #e94560;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            margin-top: 10px;
        }
        
        .menu-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .menu-card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .menu-card:hover {
            transform: translateY(-5px);
            background: rgba(255,255,255,0.2);
            border-color: #667eea;
        }
        
        .menu-icon {
            font-size: 40px;
            margin-bottom: 10px;
        }
        
        .menu-title {
            font-weight: bold;
            font-size: 14px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-label {
            font-size: 14px;
            color: #aaa;
            margin-bottom: 10px;
        }
        
        .stat-value {
            font-size: 28px;
            font-weight: bold;
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
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.1);
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
        
        select, input {
            padding: 12px 24px;
            border-radius: 8px;
            border: 2px solid rgba(255,255,255,0.2);
            background: rgba(0,0,0,0.5);
            color: white;
            font-size: 14px;
            cursor: pointer;
        }
        
        select option {
            background: #1a1a2e;
        }
        
        .info-panel {
            background: rgba(0,0,0,0.5);
            border-left: 4px solid #f59e0b;
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
        
        canvas {
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="title">🚀 BTC Dump Pro - Demo Mode</div>
            <div style="margin-top: 10px;">Working offline with simulated data</div>
            <div class="demo-badge">📡 OFFLINE DEMO MODE</div>
            <div class="info-panel" style="margin-top: 15px;">
                💡 <strong>Demo Mode Active:</strong> Using simulated data since internet connection is unstable.<br>
                All features work normally with realistic demo data. Train the model to see predictions!
            </div>
        </div>
        
        <div class="menu-grid">
            <div class="menu-card" onclick="showTimeframeModal()">
                <div class="menu-icon">📊</div>
                <div class="menu-title">1. Select Timeframe</div>
            </div>
            <div class="menu-card" onclick="trainModel()">
                <div class="menu-icon">🧠</div>
                <div class="menu-title">2. Train & Predict</div>
            </div>
            <div class="menu-card" onclick="refreshData()">
                <div class="menu-icon">🔄</div>
                <div class="menu-title">3. Refresh Data</div>
            </div>
            <div class="menu-card" onclick="showPortfolioModal()">
                <div class="menu-icon">💰</div>
                <div class="menu-title">4. Portfolio Status</div>
            </div>
        </div>
        
        <div class="stats-grid" id="statsGrid">
            <div class="stat-card">
                <div class="stat-label">💰 Current Price (Demo)</div>
                <div class="stat-value" id="price">$0</div>
                <div class="stat-change" id="priceChange">Loading...</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">🔮 AI Prediction</div>
                <div class="stat-value" id="prediction">$0</div>
                <div class="stat-change" id="targetChange">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">🎯 Signal</div>
                <div id="signalBadge">---</div>
                <div class="stat-change" id="confidence">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">💼 Portfolio Value</div>
                <div class="stat-value" id="portfolio">$1,000</div>
                <div class="stat-change" id="roi">ROI: 0%</div>
            </div>
        </div>
        
        <div class="chart-container">
            <canvas id="priceChart" height="100"></canvas>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Technical Indicators</div>
                <div id="indicators">Loading...</div>
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
    
    <div id="portfolioModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); justify-content:center; align-items:center; z-index:1000;">
        <div style="background:#1a1a2e; padding:30px; border-radius:15px; max-width:400px;">
            <h2>💰 Portfolio Management</h2>
            <p>Current: $<span id="currentPortfolio">0</span></p>
            <input type="number" id="newAmount" placeholder="Enter new amount" style="width:100%; margin:10px 0;">
            <button onclick="updatePortfolio()">Update</button>
            <button onclick="closeModal()">Cancel</button>
        </div>
    </div>
    
    <script>
        let chart;
        let priceData = [];
        let timeData = [];
        
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
            document.getElementById('price').innerHTML = '$' + data.current_price.toLocaleString();
            document.getElementById('prediction').innerHTML = '$' + data.prediction.toLocaleString();
            document.getElementById('portfolio').innerHTML = '$' + data.portfolio.current_capital.toLocaleString();
            
            const changePercent = data.change_percent;
            const changeHtml = changePercent >= 0 ? 
                `<span class="positive">▲ +${changePercent.toFixed(2)}%</span>` : 
                `<span class="negative">▼ ${changePercent.toFixed(2)}%</span>`;
            document.getElementById('priceChange').innerHTML = changeHtml;
            
            const targetChange = ((data.prediction - data.current_price) / data.current_price * 100);
            document.getElementById('targetChange').innerHTML = `Target: ${targetChange >= 0 ? '+' : ''}${targetChange.toFixed(2)}%`;
            
            document.getElementById('signalBadge').innerHTML = `<div class="signal-badge signal-${data.signal.replace(' ', '_')}">${data.signal}</div>`;
            document.getElementById('confidence').innerHTML = `Confidence: ${data.confidence}%`;
            document.getElementById('roi').innerHTML = `ROI: ${data.portfolio.roi_percentage >= 0 ? '+' : ''}${data.portfolio.roi_percentage.toFixed(2)}%`;
            
            document.getElementById('indicators').innerHTML = `
                <div><strong>RSI:</strong> ${data.rsi.toFixed(1)}</div>
                <div><strong>MACD:</strong> ${data.macd.toFixed(4)}</div>
                <div><strong>ADX:</strong> ${data.adx.toFixed(1)}</div>
                <div><strong>Volume Ratio:</strong> ${data.volume_ratio.toFixed(2)}x</div>
            `;
            
            document.getElementById('modelStats').innerHTML = `
                <div><strong>Model Error:</strong> ${(data.model_error * 100).toFixed(2)}%</div>
                <div><strong>Timeframe:</strong> ${data.timeframe}</div>
                <div><strong>Last Update:</strong> ${data.last_update}</div>
            `;
            
            // Update chart
            if (data.chart_data && data.chart_data.prices) {
                priceData = data.chart_data.prices;
                timeData = data.chart_data.timestamps;
                updateChart();
            }
        }
        
        function updateChart() {
            const ctx = document.getElementById('priceChart').getContext('2d');
            if (chart) chart.destroy();
            
            chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: timeData,
                    datasets: [{
                        label: 'BTC Price (Demo)',
                        data: priceData,
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { labels: { color: 'white' } }
                    },
                    scales: {
                        y: { grid: { color: 'rgba(255,255,255,0.1)' }, ticks: { color: 'white' } },
                        x: { grid: { color: 'rgba(255,255,255,0.1)' }, ticks: { color: 'white', maxRotation: 45, autoSkip: true } }
                    }
                }
            });
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
                    alert('❌ Training failed: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                alert('❌ Error: ' + error.message);
            } finally {
                hideLoading();
            }
        }
        
        async function refreshData() {
            showLoading();
            await fetchData();
            hideLoading();
            alert('Data refreshed!');
        }
        
        function showTimeframeModal() {
            const tf = prompt('Select Timeframe:\n1 = 5 minutes\n2 = 30 minutes\n3 = 1 hour\n4 = 4 hours\n5 = 1 day', '3');
            if (tf) {
                fetch(`/api/timeframe/${tf}`, { method: 'POST' })
                    .then(() => fetchData())
                    .catch(console.error);
            }
        }
        
        function showPortfolioModal() {
            document.getElementById('currentPortfolio').innerText = document.getElementById('portfolio').innerText.replace('$', '');
            document.getElementById('portfolioModal').style.display = 'flex';
        }
        
        async function updatePortfolio() {
            const amount = parseFloat(document.getElementById('newAmount').value);
            if (amount && amount >= 100) {
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
                        closeModal();
                        fetchData();
                    }
                } catch (error) {
                    alert('Error updating portfolio');
                } finally {
                    hideLoading();
                }
            } else {
                alert('Please enter a valid amount (minimum $100)');
            }
        }
        
        function closeModal() {
            document.getElementById('portfolioModal').style.display = 'none';
        }
        
        function showLoading() {
            // Simple loading indicator
            document.body.style.cursor = 'wait';
        }
        
        function hideLoading() {
            document.body.style.cursor = 'default';
        }
        
        // Initial load
        fetchData();
        setInterval(fetchData, 30000);
    </script>
</body>
</html>
'''

# API Routes
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/data')
def get_data():
    try:
        predictor.fetch_data()
        indicators = predictor.get_indicators()
        prediction = predictor.predict()
        current_price = predictor.current_price
        signal, confidence = predictor.generate_signal(current_price, prediction, 
                                                       indicators['rsi'], indicators['macd'], 
                                                       indicators['macd_signal'], indicators['adx'], 
                                                       indicators['volume_ratio'])
        
        # Generate chart data
        import random
        history = []
        timestamps = []
        price_history = [current_price * (1 + random.uniform(-0.05, 0.05)) for _ in range(50)]
        
        for i in range(50):
            timestamps.append(f"{i} min ago")
        
        return jsonify({
            'current_price': current_price,
            'prediction': prediction,
            'signal': signal,
            'confidence': confidence,
            'rsi': indicators['rsi'],
            'macd': indicators['macd'],
            'macd_signal': indicators['macd_signal'],
            'adx': indicators['adx'],
            'volume_ratio': indicators['volume_ratio'],
            'model_error': 0.025,
            'last_update': predictor.last_update,
            'timeframe': predictor.interval,
            'portfolio': predictor.get_portfolio_info(),
            'change_percent': random.uniform(-2, 2),
            'chart_data': {
                'timestamps': timestamps,
                'prices': price_history
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/train', methods=['POST'])
def train_model():
    try:
        # Simulate training
        time.sleep(2)
        predictor.models = {'error': 0.025}
        return jsonify({'success': True, 'error': 0.025})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/timeframe/<tf>', methods=['POST'])
def change_timeframe(tf):
    timeframe_map = {'1': '5m', '2': '30m', '3': '1h', '4': '4h', '5': '1d'}
    predictor.interval = timeframe_map.get(tf, '1h')
    return jsonify({'success': True})

@app.route('/api/portfolio', methods=['POST'])
def update_portfolio():
    try:
        data = request.json
        amount = float(data.get('amount', 0))
        if predictor.set_portfolio_amount(amount):
            return jsonify({'success': True})
        return jsonify({'success': False})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("="*60)
    print("🚀 BTC Dump Pro - OFFLINE DEMO MODE")
    print("="*60)
    print("\n📡 This version works WITHOUT internet connection")
    print("💡 Using simulated data for demonstration")
    print("\n📊 Open your browser: http://localhost:5000")
    print("⚡ Press Ctrl+C to stop the server")
    print("="*60)
    app.run(debug=True, host='0.0.0.0', port=5000)