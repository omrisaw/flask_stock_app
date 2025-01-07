from flask import Flask, jsonify, request, render_template
import requests

app = Flask(__name__)
API_KEY = "ctujh4hr01qg98tdfqe0ctujh4hr01qg98tdfqeg"

# Root route to serve the homepage
@app.route("/")
def home():
    return render_template("index.html")

# Stocks route to fetch stock data
@app.route("/stocks", methods=["GET"])
def get_stock_data():
    symbols = request.args.get("symbols", "").split(",")
    stock_data = []

    for symbol in symbols:
        try:
            response = requests.get(f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}")
            if response.status_code == 200:
                data = response.json()
                if data.get("c") is not None:  # Check if price is valid
                    stock_data.append({
                        "symbol": symbol,
                        "price": data.get("c", 0),
                        "change": data.get("d", 0)
                    })
                else:
                    stock_data.append({"symbol": symbol, "error": "Invalid data from API"})
            else:
                stock_data.append({"symbol": symbol, "error": "Failed to fetch data from API"})
        except Exception as e:
            stock_data.append({"symbol": symbol, "error": str(e)})

    return jsonify(stock_data)

if __name__ == "__main__":
    app.run(debug=True)
