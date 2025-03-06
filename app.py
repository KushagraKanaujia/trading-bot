import os
import logging
import json
import openai  
import alpaca_trade_api as tradeapi
import requests
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd

# ✅ Load API keys from .env file
load_dotenv()
API_KEY = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")
BASE_URL = os.getenv("APCA_API_BASE_URL", "https://paper-api.alpaca.markets")
MARKET_DATA_URL = os.getenv("APCA_MARKET_DATA_URL", "https://data.alpaca.markets")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Ensure API credentials are loaded
if not API_KEY or not API_SECRET or not BASE_URL or not OPENAI_API_KEY:
    raise ValueError("\u274c API keys are missing. Make sure your .env file is set up correctly.")

# Initialize APIs
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')
openai.api_key = OPENAI_API_KEY

# Flask app setup
app = Flask(__name__)

# Store price history & trade history
price_history = {}
trade_history = []

# Configurations
BUY_THRESHOLD = -2.0  # Buy when price drops by 2%
SELL_THRESHOLD = 2.5   # Sell when price increases by 2.5%
TRADE_AMOUNT = 1       # Number of stocks to buy/sell
MAX_HISTORY = 20       # Max historical data for analysis

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ Automatic price tracking every 10 seconds
def auto_track_prices():
    global price_history
    tracked_symbols = list(price_history.keys())
    headers = {
        "APCA-API-KEY-ID": API_KEY,
        "APCA-API-SECRET-KEY": API_SECRET
    }
    for symbol in tracked_symbols:
        try:
            response = requests.get(f"{MARKET_DATA_URL}/v2/stocks/{symbol}/bars/latest", headers=headers)
            data = response.json()
            if "bars" in data and data["bars"]:
                latest_price = data["bars"][0]["c"]
                price_history[symbol].append(latest_price)
                if len(price_history[symbol]) > MAX_HISTORY:
                    price_history[symbol] = price_history[symbol][-MAX_HISTORY:]
                logging.info(f"Auto-updated {symbol}: ${latest_price}")
        except Exception as e:
            logging.error(f"Error auto-updating {symbol}: {e}")

# Start background scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(auto_track_prices, 'interval', seconds=10)
scheduler.start()

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/market_status')
def market_status():
    try:
        clock = api.get_clock()
        account = api.get_account()
        return jsonify({
            "status": "Open" if clock.is_open else "Closed",
            "balance": account.equity
        })
    except Exception as e:
        logging.error(f"Error fetching market status: {e}")
        return jsonify({"error": "Failed to fetch market status"})

@app.route('/track/<symbol>')
def track_price(symbol):
    try:
        headers = {
            "APCA-API-KEY-ID": API_KEY,
            "APCA-API-SECRET-KEY": API_SECRET
        }
        response = requests.get(f"{MARKET_DATA_URL}/v2/stocks/{symbol}/bars/latest", headers=headers)
        data = response.json()

        if "bars" not in data or not data["bars"]:
            return jsonify({"error": "No market data available for this stock."})

        latest_price = data["bars"][0]["c"]

        if symbol not in price_history:
            price_history[symbol] = []
        price_history[symbol].append(latest_price)
        if len(price_history[symbol]) > MAX_HISTORY:
            price_history[symbol] = price_history[symbol][-MAX_HISTORY:]

        logging.info(f"Tracked {symbol} at ${latest_price}")
        return jsonify({"status": "Price recorded", "symbol": symbol, "latest_price": latest_price, "history": price_history[symbol]})
    except Exception as e:
        logging.error(f"Error tracking price: {e}")
        return jsonify({"error": str(e)})

@app.route('/trade/<symbol>')
def trade(symbol):
    try:
        if symbol not in price_history or len(price_history[symbol]) < 2:
            return jsonify({"error": "Not enough data to make a decision. Keep tracking prices."})

        headers = {
            "APCA-API-KEY-ID": API_KEY,
            "APCA-API-SECRET-KEY": API_SECRET
        }
        response = requests.get(f"{MARKET_DATA_URL}/v2/stocks/{symbol}/bars/latest", headers=headers)
        data = response.json()
        
        if "bars" not in data or not data["bars"]:
            return jsonify({"error": "No market data available."})

        latest_price = data["bars"][0]["c"]
        prev_price = price_history[symbol][-2]
        price_change = ((latest_price - prev_price) / prev_price) * 100
        price_history[symbol].append(latest_price)

        account = api.get_account()
        if not api.get_clock().is_open:
            return jsonify({"status": "Market closed"})

        if price_change <= BUY_THRESHOLD and float(account.buying_power) > latest_price * TRADE_AMOUNT:
            order = api.submit_order(symbol, TRADE_AMOUNT, "buy", "market", "gtc")
            trade_history.append({"action": "BUY", "symbol": symbol, "price": latest_price, "order_id": order.id})
            return jsonify({"status": "BUY order placed", "symbol": symbol, "price": latest_price})
        elif price_change >= SELL_THRESHOLD:
            for position in api.list_positions():
                if position.symbol == symbol:
                    order = api.submit_order(symbol, int(position.qty), "sell", "market", "gtc")
                    trade_history.append({"action": "SELL", "symbol": symbol, "price": latest_price, "order_id": order.id})
                    return jsonify({"status": "SELL order placed", "symbol": symbol, "price": latest_price})

        return jsonify({"status": "No trade executed", "price_change": price_change})
    except Exception as e:
        logging.error(f"Trade error: {e}")
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
