"""Flask dashboard for the trading bot.

Two modes:
  * LIVE (paper) mode  - set APCA_API_KEY_ID / APCA_API_SECRET_KEY (Alpaca paper keys)
  * DEMO mode          - automatic when keys are missing, or force with DEMO_MODE=1.
                         Uses a simulated broker and simulated prices, needs no accounts.
"""

import os
import logging
import random
import zlib

from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

# Load API keys from .env file (if present)
load_dotenv()
API_KEY = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")
BASE_URL = os.getenv("APCA_API_BASE_URL", "https://paper-api.alpaca.markets")
MARKET_DATA_URL = os.getenv("APCA_MARKET_DATA_URL", "https://data.alpaca.markets")

PLACEHOLDER_KEYS = {"", "your_api_key_here", "your_api_secret_here"}
DEMO_MODE = (
    os.getenv("DEMO_MODE", "").lower() in {"1", "true", "yes"}
    or (API_KEY or "") in PLACEHOLDER_KEYS
    or (API_SECRET or "") in PLACEHOLDER_KEYS
)

# Configurations
BUY_THRESHOLD = -2.0  # Buy when price drops by 2%
SELL_THRESHOLD = 2.5   # Sell when price increases by 2.5%
TRADE_AMOUNT = 1       # Number of stocks to buy/sell
MAX_HISTORY = 20       # Max historical data for analysis

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)

# Store price history & trade history
price_history = {}
trade_history = []


class DemoBroker:
    """Tiny in-memory stand-in for Alpaca so the app runs with zero keys.

    Prices follow a random walk with deliberately large ticks (~2% std dev)
    so the -2% / +2.5% thresholds actually trigger during a short demo.
    """

    def __init__(self, cash: float = 100_000.0):
        self.cash = cash
        self.positions = {}  # symbol -> qty
        self.prices = {}

    def latest_price(self, symbol: str) -> float:
        if symbol not in self.prices:
            # Deterministic starting price per symbol, between $20 and $500
            self.prices[symbol] = round(20 + (zlib.crc32(symbol.encode()) % 48000) / 100, 2)
        else:
            move = random.gauss(0, 0.02)
            self.prices[symbol] = round(max(1.0, self.prices[symbol] * (1 + move)), 2)
        return self.prices[symbol]

    def equity(self) -> float:
        held = sum(qty * self.prices.get(sym, 0) for sym, qty in self.positions.items())
        return round(self.cash + held, 2)

    def buy(self, symbol: str, qty: int, price: float):
        self.cash -= qty * price
        self.positions[symbol] = self.positions.get(symbol, 0) + qty

    def sell_all(self, symbol: str, price: float) -> int:
        qty = self.positions.pop(symbol, 0)
        self.cash += qty * price
        return qty


if DEMO_MODE:
    logging.info("Running in DEMO mode: simulated broker + simulated prices (no API keys needed).")
    broker = DemoBroker()
    api = None
else:
    import requests
    import alpaca_trade_api as tradeapi

    broker = None
    api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')


def fetch_latest_price(symbol: str):
    """Return the latest close for a symbol, or None if unavailable."""
    if DEMO_MODE:
        return broker.latest_price(symbol)
    headers = {"APCA-API-KEY-ID": API_KEY, "APCA-API-SECRET-KEY": API_SECRET}
    response = requests.get(f"{MARKET_DATA_URL}/v2/stocks/{symbol}/bars/latest", headers=headers, timeout=10)
    data = response.json()
    # Alpaca returns {"bar": {...}}; older code expected {"bars": [...]}. Accept both.
    bar = data.get("bar") or (data.get("bars") or [None])[0]
    return bar["c"] if bar else None


def record_price(symbol: str, price: float):
    history = price_history.setdefault(symbol, [])
    history.append(price)
    if len(history) > MAX_HISTORY:
        price_history[symbol] = history[-MAX_HISTORY:]


# Automatic price tracking every 10 seconds
def auto_track_prices():
    for symbol in list(price_history.keys()):
        try:
            latest_price = fetch_latest_price(symbol)
            if latest_price is not None:
                record_price(symbol, latest_price)
                logging.info(f"Auto-updated {symbol}: ${latest_price}")
        except Exception as e:
            logging.error(f"Error auto-updating {symbol}: {e}")


scheduler = BackgroundScheduler()
scheduler.add_job(auto_track_prices, 'interval', seconds=10)
scheduler.start()


@app.route('/')
def home():
    return render_template("index.html", demo_mode=DEMO_MODE)


@app.route('/market_status')
def market_status():
    try:
        if DEMO_MODE:
            return jsonify({"status": "Open (simulated)", "balance": broker.equity(), "demo": True})
        clock = api.get_clock()
        account = api.get_account()
        return jsonify({
            "status": "Open" if clock.is_open else "Closed",
            "balance": account.equity,
            "demo": False,
        })
    except Exception as e:
        logging.error(f"Error fetching market status: {e}")
        return jsonify({"error": "Failed to fetch market status"})


@app.route('/track/<symbol>')
def track_price(symbol):
    symbol = symbol.upper()
    try:
        latest_price = fetch_latest_price(symbol)
        if latest_price is None:
            return jsonify({"error": "No market data available for this stock."})
        record_price(symbol, latest_price)
        logging.info(f"Tracked {symbol} at ${latest_price}")
        return jsonify({"status": "Price recorded", "symbol": symbol,
                        "latest_price": latest_price, "history": price_history[symbol]})
    except Exception as e:
        logging.error(f"Error tracking price: {e}")
        return jsonify({"error": str(e)})


@app.route('/history/<symbol>')
def history(symbol):
    symbol = symbol.upper()
    return jsonify({"symbol": symbol, "history": price_history.get(symbol, []), "trades": trade_history})


@app.route('/trade/<symbol>')
def trade(symbol):
    symbol = symbol.upper()
    try:
        if symbol not in price_history or len(price_history[symbol]) < 2:
            return jsonify({"error": "Not enough data to make a decision. Keep tracking prices."})

        latest_price = fetch_latest_price(symbol)
        if latest_price is None:
            return jsonify({"error": "No market data available."})

        prev_price = price_history[symbol][-1]
        price_change = ((latest_price - prev_price) / prev_price) * 100
        record_price(symbol, latest_price)

        if DEMO_MODE:
            buying_power = broker.cash
            held = broker.positions.get(symbol, 0)
        else:
            if not api.get_clock().is_open:
                return jsonify({"status": "Market closed"})
            buying_power = float(api.get_account().buying_power)
            held = next((int(p.qty) for p in api.list_positions() if p.symbol == symbol), 0)

        if price_change <= BUY_THRESHOLD and buying_power > latest_price * TRADE_AMOUNT:
            if DEMO_MODE:
                broker.buy(symbol, TRADE_AMOUNT, latest_price)
                order_id = f"demo-{len(trade_history) + 1}"
            else:
                order_id = api.submit_order(symbol, TRADE_AMOUNT, "buy", "market", "gtc").id
            trade_history.append({"action": "BUY", "symbol": symbol, "price": latest_price, "order_id": order_id})
            return jsonify({"status": "BUY order placed", "symbol": symbol, "price": latest_price,
                            "price_change": price_change})
        elif price_change >= SELL_THRESHOLD and held > 0:
            if DEMO_MODE:
                broker.sell_all(symbol, latest_price)
                order_id = f"demo-{len(trade_history) + 1}"
            else:
                order_id = api.submit_order(symbol, held, "sell", "market", "gtc").id
            trade_history.append({"action": "SELL", "symbol": symbol, "price": latest_price, "order_id": order_id})
            return jsonify({"status": "SELL order placed", "symbol": symbol, "price": latest_price,
                            "price_change": price_change})

        return jsonify({"status": "No trade executed", "price_change": price_change, "price": latest_price})
    except Exception as e:
        logging.error(f"Trade error: {e}")
        return jsonify({"error": str(e)})


if __name__ == '__main__':
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
        use_reloader=False,  # the reloader would start the price scheduler twice
    )
