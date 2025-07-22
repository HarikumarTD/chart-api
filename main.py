from flask import Flask, request, jsonify
import yfinance as yf
import mplfinance as mpf
import pandas as pd
import io
import base64

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

        required_columns = ["Open", "High", "Low", "Close"]
        if data.empty or not all(col in data.columns for col in required_columns):
            return jsonify({"status": "error", "message": "Required OHLC data missing."})

        if not all(pd.api.types.is_numeric_dtype(data[col]) for col in required_columns):
            return jsonify({"status": "error", "message": "Data must be numeric type."})

        fig, _ = mpf.plot(data, type='candle', style='charles', returnfig=True)
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        base64_img = base64.b64encode(buf.read()).decode("utf-8")
        return jsonify({"status": "success", "chart": base64_img})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
