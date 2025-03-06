import os
import logging
import json
import openai  
import alpaca_trade_api as tradeapi
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
import pandas as pd

# ✅ Load API keys from .env file
load_dotenv()
API_KEY = os.getenv("APCA_API_KEY_ID") or "YOUR_ALPACA_API_KEY"
API_SECRET = os.getenv("APCA_API_SECRET_KEY") or "YOUR_ALPACA_SECRET_KEY"
BASE_URL = os.getenv("APCA_API_BASE_URL") or "https://paper-api.alpaca.markets"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or "YOUR_OPENAI_KEY"

# Ensure API credentials are loaded
if not API_KEY or not API_SECRET or not BASE_URL or not OPENAI_API_KEY:
    raise ValueError("❌ API keys are missing. Make sure your .env file is set up correctly.")

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


@app.route('/')
def home():
    """ Loads the frontend UI """
    return render_template("index.html")


@app.route('/market_status')
def market_status():
    """ Returns market open/close status and account balance """
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
    """ Tracks stock prices over time """
    try:
        # ✅ Fix for fetching stock bars properly
        bars = api.get_latest_bar(symbol)  # FIXED METHOD
        if not bars:
            return jsonify({"error": "No market data available for this stock."})

        latest_price = bars.c  # Closing price

        if symbol not in price_history:
            price_history[symbol] = []
        price_history[symbol].append(latest_price)

        # ✅ Keep history limited to prevent overflow
        if len(price_history[symbol]) > MAX_HISTORY:
            price_history[symbol] = price_history[symbol][-MAX_HISTORY:]

        logging.info(f"Tracked {symbol} at ${latest_price}")

        return jsonify({
            "status": "Price recorded",
            "symbol": symbol,
            "latest_price": latest_price,
            "history": price_history[symbol]
        })

    except Exception as e:
        logging.error(f"Error tracking price: {e}")
        return jsonify({"error": str(e)})


@app.route('/predict/<symbol>')
def predict_trade(symbol):
    """ Uses LLM to predict trade action based on history """
    try:
        if symbol not in price_history or len(price_history[symbol]) < 5:
            return jsonify({"error": "Not enough historical data to predict. Keep tracking prices."})

        # ✅ Format price data for GPT input
        price_data = json.dumps(price_history[symbol])

        # ✅ LLM Query
        prompt = f"""
        You are a stock trading AI. Analyze this past price data:
        {price_data}
        
        Based on the trend, should the user:
        - Buy?
        - Sell?
        - Hold?

        Provide a concise, data-backed explanation.
        """
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are a financial trading expert."},
                      {"role": "user", "content": prompt}]
        )
        prediction = response["choices"][0]["message"]["content"]

        return jsonify({"prediction": prediction})

    except Exception as e:
        logging.error(f"Error predicting trade: {e}")
        return jsonify({"error": str(e)})


@app.route('/trade/<symbol>')
def trade(symbol):
    """ Smart trading based on price history """
    try:
        if symbol not in price_history or len(price_history[symbol]) < 2:
            return jsonify({"error": "Not enough data to make a decision. Keep tracking prices."})

        # ✅ Fix for fetching stock bars properly
        bars = api.get_latest_bar(symbol)
        if not bars:
            return jsonify({"error": "No market data available."})

        latest_price = bars.c
        prev_price = price_history[symbol][-2]
        price_change = ((latest_price - prev_price) / prev_price) * 100  # Percentage change

        price_history[symbol].append(latest_price)
        account = api.get_account()

        if not api.get_clock().is_open:
            return jsonify({"status": "Market closed"})

        # ✅ Buy condition
        if price_change <= BUY_THRESHOLD and float(account.buying_power) > latest_price * TRADE_AMOUNT:
            order = api.submit_order(symbol, TRADE_AMOUNT, "buy", "market", "gtc")
            trade_history.append({"action": "BUY", "symbol": symbol, "price": latest_price, "order_id": order.id})
            logging.info(f"BUY order placed for {symbol} at ${latest_price}")
            return jsonify({"status": "BUY order placed", "symbol": symbol, "price": latest_price})

        # ✅ Sell condition
        elif price_change >= SELL_THRESHOLD:
            for position in api.list_positions():
                if position.symbol == symbol:
                    order = api.submit_order(symbol, int(position.qty), "sell", "market", "gtc")
                    trade_history.append({"action": "SELL", "symbol": symbol, "price": latest_price, "order_id": order.id})
                    logging.info(f"SELL order placed for {symbol} at ${latest_price}")
                    return jsonify({"status": "SELL order placed", "symbol": symbol, "price": latest_price})

        return jsonify({"status": "No trade executed", "price_change": price_change})

    except Exception as e:
        logging.error(f"Trade error: {e}")
        return jsonify({"error": str(e)})


@app.route('/history')
def trade_history_view():
    """ Returns the trade history """
    return jsonify(trade_history)


if __name__ == '__main__':
    app.run(debug=True)
