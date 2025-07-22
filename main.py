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

        # 🔓 Fix: Flatten MultiIndex columns if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # 🐞 Debug log: Return columns if missing
        expected_cols = ["Open", "High", "Low", "Close"]
        actual_cols = data.columns.tolist()
        missing = [col for col in expected_cols if col not in actual_cols]
        if missing:
            return jsonify({
                "status": "error",
                "message": f"Missing columns: {', '.join(missing)}",
                "columns_received": actual_cols
            })

        # 🧼 Ensure numeric types
        for col in expected_cols:
            data[col] = pd.to_numeric(data[col], errors="coerce")
            if data[col].isnull().any():
                return jsonify({"status": "error", "message": f"Column '{col}' contains non-numeric values."})

        # 🧠 Make sure index is datetime
        data.index = pd.to_datetime(data.index)

        # 📈 Generate chart
        fig, _ = mpf.plot(data, type='candle', style='charles', returnfig=True)
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        base64_img = base64.b64encode(buf.read()).decode("utf-8")

        return jsonify({"status": "success", "chart": base64_img})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
