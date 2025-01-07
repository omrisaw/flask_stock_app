from flask import Flask, jsonify, request
import requests

app = Flask(__name__)
API_KEY = "ctujh4hr01qg98tdfqe0ctujh4hr01qg98tdfqeg"

@app.route("/", methods=["GET"])
def get_stock_data():
    symbols = request.args.get("symbols", "AAPL,GOOGL,AMZN,MSFT").split(",")
    stock_data = []

    for symbol in symbols:
        response = requests.get(f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}")
        if response.status_code == 200:
            data = response.json()
            stock_data.append({
                "symbol": symbol,
                "price": data.get("c", 0),
                "change": data.get("d", 0)
            })
        else:
            stock_data.append({"symbol": symbol, "error": "Failed to fetch data"})

    return jsonify(stock_data)

if __name__ == "__main__":
    app.run(debug=True)
