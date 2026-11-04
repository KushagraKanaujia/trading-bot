# Trading Bot

A Python trading bot that watches stock prices, buys dips and sells pops through Alpaca paper trading, backed by a tested risk-management library and an options-pricing experiment (Black-Scholes vs a neural network).

[![Live demo](https://img.shields.io/badge/Live%20demo-kush--trading--bot.netlify.app-00C7B7?logo=netlify&logoColor=white)](https://kush-trading-bot.netlify.app)
[![Open in GitHub Codespaces](https://img.shields.io/badge/Open%20in-Codespaces-181717?logo=github)](https://codespaces.new/KushagraKanaujia/trading-bot?quickstart=1)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Try it in one click

| Option | What you get | Needs |
| --- | --- | --- |
| **[Live demo](https://kush-trading-bot.netlify.app)** | In-browser version of the strategy on simulated prices, a position-sizing calculator, and the options-pricing results stored in this repo | Nothing |
| **[Open in Codespaces](https://codespaces.new/KushagraKanaujia/trading-bot?quickstart=1)** | The real Flask app and test suite in a cloud VS Code. Dependencies install automatically, the tests run, and the dashboard starts in **demo mode** on port 5000 | A GitHub account (Codespaces has a free monthly allowance) |

No API keys are needed for either. When `APCA_API_KEY_ID` / `APCA_API_SECRET_KEY` are missing, the app switches to a simulated broker with a $100,000 in-memory account and random-walk prices.

## What it does

1. **Flask dashboard (`app.py`, `templates/index.html`)**
   Enter a symbol, track its price, and run the strategy. Prices are re-polled every 10 seconds in the background.
   - Rule: if the price **dropped 2% or more** since the last check, buy 1 share; if it **rose 2.5% or more**, sell the position.
   - With Alpaca paper keys it places real paper orders; without keys it runs in demo mode.
2. **Risk management library (`src/risk/`)**
   - `PositionSizer`: fixed %, ATR-based and half-Kelly sizing; it picks the smallest.
   - `StopLossManager`: stop-loss (2%), take-profit (5%), trailing stop (3%), time stop.
   - `PortfolioRisk`: exposure limit, return correlation between holdings, historical VaR, portfolio beta.
   - `RiskManager`: runs the pre-trade checks (daily-loss and drawdown limits, position size, exposure, correlation).
3. **Database models (`src/models/`)**: SQLAlchemy models for trades, positions, price history, performance metrics and ML model metadata. SQLite by default, PostgreSQL via `DATABASE_URL`.
4. **Options-pricing experiment (root scripts)**
   `options_data.py` (pull an AAPL chain with yfinance) → `black_scholes.py` → `train_nn.py` (small PyTorch MLP on strike + implied volatility) → `compare_models.py` → `trade_options.py` (BUY/SELL/HOLD when the network's price differs from the last trade by more than $0.50). The CSVs and `option_pricing_nn.pth` from one run are committed. Note that the network is evaluated on the same rows it was mostly trained on.

## How it works

```
 browser ──► Flask (app.py) ──► price source ──► rule: Δ ≤ -2% buy / Δ ≥ +2.5% sell ──► broker
                                 │                                                      │
                     Alpaca market data API                                Alpaca paper API
                     or DemoBroker random walk                             or DemoBroker (in memory)

 src/risk/*  ── position sizing, stops and portfolio checks (used by examples/basic_usage.py and the tests)
```

## Tech stack

Python 3.10+, Flask, APScheduler, alpaca-trade-api, SQLAlchemy, Pydantic Settings, NumPy, pandas, SciPy, PyTorch, scikit-learn, yfinance, pytest. Dashboard uses Bootstrap 5 + Chart.js; the static demo uses Pico CSS + Chart.js.

## Run locally

```bash
git clone https://github.com/KushagraKanaujia/trading-bot.git
cd trading-bot
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

python -m pytest -q             # 50 tests
DEMO_MODE=1 python app.py       # dashboard at http://127.0.0.1:5000, no keys needed
python examples/basic_usage.py  # risk manager walkthrough
```

To use Alpaca paper trading, create free paper keys at [alpaca.markets](https://alpaca.markets), then:

```bash
cp .env.example .env   # fill in APCA_API_KEY_ID / APCA_API_SECRET_KEY
python app.py
```

Risk settings (`MAX_POSITION_SIZE`, `STOP_LOSS_PERCENTAGE`, `DAILY_LOSS_LIMIT`, ...) are read from `.env` by `src/config/settings.py`. See [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) and [docs/RISK_MANAGEMENT.md](docs/RISK_MANAGEMENT.md).

The static demo lives in `site/` and is plain HTML; open `site/index.html` through any static server (e.g. `python -m http.server -d site`).

## Project layout

```
app.py                 Flask dashboard + strategy (live or demo mode)
templates/index.html   Dashboard UI
src/config/            Settings loaded from env / .env
src/models/            SQLAlchemy models
src/risk/              Position sizing, stops, portfolio risk, RiskManager
src/strategies/base.py Base class for new strategies
tests/                 pytest suite
examples/              Usage example
*.py (root)            Options-pricing pipeline scripts
site/                  Static demo deployed to Netlify
.devcontainer/         Codespaces / Dev Containers config
```

## Credits

- [Pico CSS](https://github.com/picocss/pico) (MIT) for the static demo styling
- [Chart.js](https://github.com/chartjs/Chart.js) (MIT) for charts
- [Bootstrap](https://github.com/twbs/bootstrap) (MIT) for the dashboard
- [devcontainers/images](https://github.com/devcontainers/images) (MIT) Python base image for Codespaces
- [shields.io](https://shields.io) (CC0) badges
- [Alpaca](https://alpaca.markets) paper trading API

## Disclaimer

Educational project, not financial advice. Trading involves risk of loss; use paper trading.

## License

MIT, see [LICENSE](LICENSE).
