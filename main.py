from flask import Flask, request, jsonify
import yfinance as yf
import mplfinance as mpf
import io
import base64
import pandas as pd

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Chart API is running. Use /chart?symbol=AAPL"

@app.route("/chart")
def chart():
    symbol = request.args.get("symbol")
    if not symbol:
        return jsonify({"status": "error", "message": "Missing symbol"}), 400

    try:
        data = yf.download(symbol, period="5d", interval="1d")

        if data.empty:
            return jsonify({"status": "error", "message": "No data returned for symbol."})

        # Ensure required columns exist
        required_columns = ["Open", "High", "Low", "Close"]
        for col in required_columns:
            if col not in data.columns:
                return jsonify({"status": "error", "message": f"Missing column '{col}' in data."})

        # Convert to numeric and drop rows with invalid values
        data[required_columns] = data[required_columns].apply(pd.to_numeric, errors='coerce')
        data.dropna(subset=required_columns, inplace=True)

        if data.empty:
            return jsonify({"status": "error", "message": "Cleaned data is empty. Symbol might be invalid or corrupted."})

        # Generate the chart
        fig, _ = mpf.plot(data, type='candle', style='charles', returnfig=True)
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        base64_img = base64.b64encode(buf.read()).decode('utf-8')

        return jsonify({"status": "success", "chart": base64_img})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
