{\rtf1\ansi\ansicpg1252\cocoartf2818
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww21400\viewh16220\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 from flask import Flask, jsonify, request\
import requests\
\
app = Flask(__name__)\
API_KEY = "ctujh4hr01qg98tdfqe0ctujh4hr01qg98tdfqeg"\
\
@app.route("/stocks", methods=["GET"])\
def get_stock_data():\
    symbols = request.args.get("symbols", "AAPL,GOOGL,AMZN,MSFT").split(",")\
    stock_data = []\
\
    for symbol in symbols:\
        response = requests.get(f"https://finnhub.io/api/v1/quote?symbol=\{symbol\}&token=\{API_KEY\}")\
        if response.status_code == 200:\
            data = response.json()\
            stock_data.append(\{\
                "symbol": symbol,\
                "price": data.get("c", 0),\
                "change": data.get("d", 0)\
            \})\
        else:\
            stock_data.append(\{"symbol": symbol, "error": "Failed to fetch data"\})\
\
    return jsonify(stock_data)\
\
if __name__ == "__main__":\
    app.run(debug=True)\
}