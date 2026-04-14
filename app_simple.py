from flask import Flask, jsonify, render_template_string
from BTCDump import BTCPredictorPro
import logging

app = Flask(__name__)
predictor = BTCPredictorPro()

SIMPLE_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>BTC Dump Pro</title>
    <style>
        body { font-family: Arial; padding: 20px; background: #1a1a2e; color: white; }
        .card { background: #16213e; padding: 20px; border-radius: 10px; margin: 10px 0; }
        .price { font-size: 48px; color: #00ff88; }
        button { background: #e94560; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #ff6b6b; }
    </style>
</head>
<body>
    <h1>🚀 BTC Dump Pro</h1>
    <div class="card">
        <h2>Current Price</h2>
        <div class="price" id="price">Loading...</div>
    </div>
    <div class="card">
        <h2>AI Prediction</h2>
        <div id="prediction">Loading...</div>
    </div>
    <div class="card">
        <h2>Signal</h2>
        <div id="signal">Loading...</div>
    </div>
    <button onclick="train()">Train Model</button>
    <button onclick="refresh()">Refresh</button>
    
    <script>
        async function refresh() {
            const res = await fetch('/api/data');
            const data = await res.json();
            document.getElementById('price').innerText = '$' + data.current_price.toLocaleString();
            document.getElementById('prediction').innerText = '$' + data.prediction.toLocaleString();
            document.getElementById('signal').innerText = data.signal;
        }
        
        async function train() {
            alert('Training started... This may take 30 seconds');
            const res = await fetch('/api/train', {method: 'POST'});
            const data = await res.json();
            alert('Training complete! Error: ' + (data.error * 100).toFixed(2) + '%');
            refresh();
        }
        
        refresh();
        setInterval(refresh, 30000);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(SIMPLE_HTML)

@app.route('/api/data')
def get_data():
    try:
        df = predictor.fetch_data(predictor.interval)
        if df is None:
            return jsonify({'current_price': 0, 'prediction': 0, 'signal': 'NO DATA'})
        
        current_price = float(df['close'].iloc[-1])
        
        if predictor.models:
            predictor.df = predictor.indicators(df)
            X, y = predictor.features(predictor.df)
            if len(X) > 0:
                pred = predictor.predict(predictor.models, X[-1])
                return jsonify({'current_price': current_price, 'prediction': float(pred), 'signal': 'READY'})
        
        return jsonify({'current_price': current_price, 'prediction': current_price, 'signal': 'TRAIN FIRST'})
    except Exception as e:
        return jsonify({'current_price': 0, 'prediction': 0, 'signal': f'ERROR: {str(e)}'})

@app.route('/api/train', methods=['POST'])
def train():
    try:
        df = predictor.fetch_data(predictor.interval)
        predictor.df = predictor.indicators(df)
        X, y = predictor.features(predictor.df)
        predictor.models = predictor.train(X, y)
        return jsonify({'success': True, 'error': predictor.models['error']})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("Starting simplified BTC Dump Pro...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, port=5000)