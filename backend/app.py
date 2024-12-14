# trading-bot/backend/app.py

from flask import Flask, render_template, request
import json
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

def get_available_algorithms():
    log_dir = Path("logs")
    # Get all directories in logs/ folder
    algorithms = [d.name for d in log_dir.iterdir() if d.is_dir()]
    return algorithms

def load_trading_data(algorithm):
    # Path to log files
    log_dir = Path(f"logs/{algorithm}")
    db_file = log_dir / "db.json"
    today_file = log_dir / "today.json"
    
    all_trades = []
    
    # Load historical trades from db.json
    if db_file.exists():
        with open(db_file, 'r') as f:
            historical_data = json.load(f)
            all_trades.extend(historical_data.get('trades', []))
    
    # Load today's trades
    if today_file.exists():
        with open(today_file, 'r') as f:
            today_data = json.load(f)
            all_trades.extend(today_data.get('trades', []))
    
    # Format trades for display
    formatted_trades = []
    for trade in all_trades:
        formatted_trade = {
            'date': datetime.fromisoformat(trade['timestamp']).strftime('%Y-%m-%d'),
            'time': datetime.fromisoformat(trade['timestamp']).strftime('%H:%M:%S'),
            'type': trade['type'].upper(),
            'quantity': trade['details']['quantity'],
            'status': trade['status'],
            'price': trade['details'].get('filled_price', 'N/A')
        }
        formatted_trades.append(formatted_trade)
    
    # Sort trades by timestamp (newest first)
    formatted_trades.sort(key=lambda x: f"{x['date']} {x['time']}", reverse=True)
    
    return formatted_trades

@app.route('/')
def index():
    algorithms = get_available_algorithms()
    selected_algorithm = request.args.get('algorithm', algorithms[0] if algorithms else None)
    
    trades = []
    if selected_algorithm:
        trades = load_trading_data(selected_algorithm)
    
    return render_template('index.html', 
                         trades=trades, 
                         algorithms=algorithms, 
                         selected_algorithm=selected_algorithm)

if __name__ == '__main__':
    app.run(debug=True, port=8000)