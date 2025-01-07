from flask import Flask, jsonify, request, render_template
from flask_socketio import SocketIO
import requests
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app)
API_KEY = "ctujh4hr01qg98tdfqe0ctujh4hr01qg98tdfqeg"
stocks_data = {}
refresh_interval = 5  # seconds

def fetch_stock_data():
    global stocks_data
    while True:
        updated_data = {}
        for symbol in stocks_data.keys():
            try:
                response = requests.get(f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}")
                if response.status_code == 200:
                    data = response.json()
                    if data.get("c") is not None:  # Check if price is valid
                        updated_data[symbol] = {
                            "price": data.get("c", 0),
                            "change": data.get("d", 0)
                        }
                    else:
                        updated_data[symbol] = {"error": "Invalid data from API"}
                else:
                    updated_data[symbol] = {"error": f"API Error: {response.status_code} {response.text}"}
            except requests.exceptions.RequestException as e:
                updated_data[symbol] = {"error": f"Request Exception: {str(e)}"}
        stocks_data = updated_data
        socketio.emit("stock_update", stocks_data)
        time.sleep(refresh_interval)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/stocks", methods=["GET", "POST", "DELETE"])
def stocks():
    if request.method == "GET":
        # Return the current stocks_data as JSON
        return jsonify(stocks_data)

    elif request.method == "POST":
        # Add a stock
        symbol = request.json.get("symbol", "").strip().upper()
        if symbol and symbol not in stocks_data:
            stocks_data[symbol] = {"price": 0, "change": 0}  # Initialize with default values
            return jsonify({"message": f"Symbol {symbol} added successfully."}), 200
        return jsonify({"error": "Invalid symbol or already exists."}), 400

    elif request.method == "DELETE":
        # Remove a stock
        symbol = request.json.get("symbol", "").strip().upper()
        if symbol in stocks_data:
            del stocks_data[symbol]
            return jsonify({"message": f"Symbol {symbol} removed successfully."}), 200
        return jsonify({"error": "Symbol not found."}), 400


if __name__ == "__main__":
    threading.Thread(target=fetch_stock_data, daemon=True).start()
    socketio.run(app, debug=True)
