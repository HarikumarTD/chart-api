from flask import Flask, request, jsonify
import yfinance as yf
import mplfinance as mpf
import io
import base64
import pandas as pd  # Required for checking dtypes

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Chart API is running. Use /chart?symbol=AAPL"

@app.route("/chart")
def chart():
    symbol = request.args.get("symbol")
    if not symbol:
        return jsonify({"status": "error", "message": "Missing 'symbol' query param"}), 400

    try:
        # Fetch data from yfinance
        data = yf.download(symbol, period="5d", interval="1d")

        if data.empty:
            return jsonify({"status": "error", "message": "No data received."}), 400

        # Keep only necessary columns and drop NaNs
        ohlc_cols = ["Open", "High", "Low", "Close", "Volume"]
        data = data[ohlc_cols].dropna()

        # Check if all OHLC columns are numeric
        for col in ["Open", "High", "Low", "Close"]:
            if not pd.api.types.is_numeric_dtype(data[col]):
                return jsonify({"status": "error", "message": f"Column '{col}' is not numeric."}), 400

        # Create the chart
        fig, _ = mpf.plot(data, type='candle', style='charles', returnfig=True)
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        base64_img = base64.b64encode(buf.read()).decode('utf-8')

        return jsonify({"status": "success", "chart": base64_img})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
