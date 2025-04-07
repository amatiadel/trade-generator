import pandas as pd
import random
from flask import Flask, render_template_string, request
import os

# Initialize Flask app
app = Flask(__name__)

# File path to the Excel file (relative path for cloud)
file_path = "trades.xlsx"  # Must be in the same directory as the app

def load_data(file_path):
    """Load the Excel file and return the data."""
    try:
        data = pd.read_excel(file_path)
        return data
    except FileNotFoundError:
        return None

def select_trades(data, num_trades=20):
    """Select 12 random trades with a spread across hours."""
    if data is None:
        return ["Error: File not found. Check the file path."]
    
    data['Hour'] = data['Time'].apply(lambda x: x.split(':')[0])
    unique_hours = sorted(data['Hour'].unique())
    
    trades = []
    hour_trades = {}
    for hour in unique_hours:
        hour_data = data[data['Hour'] == hour]
        if not hour_data.empty:
            trade = hour_data.sample(n=1).iloc[0]
            hour_trades[hour] = f"{trade['Time']} {trade['Currency']} {trade['Direction']}"
    
    trades.extend(hour_trades.values())
    remaining = num_trades - len(trades)
    if remaining > 0:
        extra_trades = data.sample(n=remaining, replace=False)
        for _, row in extra_trades.iterrows():
            trades.append(f"{row['Time']} {trade['Currency']} {trade['Direction']}")
    
    trades_sorted = sorted(trades, key=lambda x: x.split()[0])
    return trades_sorted[:num_trades]

def generate_output(trades):
    """Generate the full output with and without direction."""
    trades_with_direction = trades
    trades_no_direction = [f"{trade.split()[0]} {trade.split()[1]}" for trade in trades]
    return trades_with_direction, trades_no_direction

# HTML template with a randomize button
html_template = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>صفقات اليوم</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: right; padding: 20px; }
        h1 { color: #333; }
        h2 { color: #555; }
        .section { margin-bottom: 20px; }
        .trade { margin: 5px 0; }
        .warning { color: red; font-weight: bold; }
        .button { padding: 10px 20px; background-color: #4CAF50; color: white; border: none; cursor: pointer; }
        .button:hover { background-color: #45a049; }
    </style>
</head>
<body>
    <h1>صفقات اليوم</h1>
    <div class="section">
        {% for trade in trades_with_direction %}
            <div class="trade">{{ trade }}</div>
        {% endfor %}
    </div>
    <div class="section">
        <h2>اوقات صفقات اليوم ستكون كتالي علشان كل واحد يكون عارف وقت صدور صفقة و يكون جاهز :</h2>
        {% for trade in trades_no_direction %}
            <div class="trade">{{ trade }}</div>
        {% endfor %}
    </div>
    <div class="warning">
        🚨 اتجاه الصفقات راح تنزل قبل وقت ب 5 دقائق علشان تكونوا عارفين الاتجاه
    </div>
    <form method="POST" action="/">
        <button type="submit" class="button">توليد صفقات جديدة</button>
    </form>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def display_trades():
    """Route to display trades in the browser, re-randomizes on POST."""
    data = load_data(file_path)
    if data is None:
        return "Error: Could not load trades.xlsx. Check the file path."
    
    trades = select_trades(data, num_trades=12)
    trades_with_direction, trades_no_direction = generate_output(trades)
    
    return render_template_string(html_template, 
                                 trades_with_direction=trades_with_direction, 
                                 trades_no_direction=trades_no_direction)

# Run the app for cloud deployment
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Render's PORT env var or default to 5000
    app.run(host='0.0.0.0', port=port, debug=False)