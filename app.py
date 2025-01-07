from flask import Flask, jsonify, request, render_template
from flask_socketio import SocketIO
import requests
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app)
API_KEY = "ctujh4hr01qg98tdfqe0ctujh4hr01qg98tdfqeg"
stocks_data = {
    "AAPL": {"price": 0, "change": 0},
    "GOOGL": {"price": 0, "change": 0},
    "AMZN": {"price": 0, "change": 0},
    "MSFT": {"price": 0, "change": 0}
}
refresh_interval = 5  # seconds
data_lock = threading.Lock()

def fetch_stock_data():
    global stocks_data
    while True:
        with data_lock:
            for symbol in stocks_data.keys():
                try:
                    print(f"Fetching data for {symbol}...")  # Debug
                    response = requests.get(f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}")
                    print(f"Response for {symbol}: {response.status_code}")  # Debug
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"Data for {symbol}: {data}")  # Debug
                    
                        if data.get("c") is not None:  # Check if current price is valid
                            stocks_data[symbol] = {
                                "price": data.get("c", 0),  # Current price
                                "change": data.get("d", 0)  # Price change
                            }
                        else:
                            stocks_data[symbol] = {"error": "Invalid data from API"}
                    else:
                        stocks_data[symbol] = {"error": f"API Error: {response.status_code}"}
                except requests.exceptions.RequestException as e:
                    stocks_data[symbol] = {"error": f"Request Exception: {str(e)}"}
            print("Updated stocks_data:", stocks_data)  # Debug
            socketio.emit("stock_update", stocks_data)
        time.sleep(refresh_interval)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/stocks", methods=["GET", "POST", "DELETE"])
def stocks():
    global stocks_data
    if request.method == "GET":
        with data_lock:
            return jsonify(stocks_data)

    elif request.method == "POST":
        symbol = request.json.get("symbol", "").strip().upper()
        if symbol:
            with data_lock:
                if symbol not in stocks_data:
                    stocks_data[symbol] = {"price": 0, "change": 0}
                    return jsonify({"message": f"Symbol {symbol} added successfully."}), 200
        return jsonify({"error": "Invalid symbol or already exists."}), 400

    elif request.method == "DELETE":
        symbol = request.json.get("symbol", "").strip().upper()
        with data_lock:
            if symbol in stocks_data:
                del stocks_data[symbol]
                return jsonify({"message": f"Symbol {symbol} removed successfully."}), 200
        return jsonify({"error": "Symbol not found."}), 400

if __name__ == "__main__":
    print("Starting app with initial stocks_data:", stocks_data)
    threading.Thread(target=fetch_stock_data, daemon=True).start()
    socketio.run(app, debug=True)
