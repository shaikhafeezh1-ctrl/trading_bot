# Trading Bot — Binance Futures Testnet (USDT-M)

A small, structured Python CLI application that places MARKET, LIMIT, and
STOP_LIMIT orders on Binance Futures Testnet, with input validation,
structured logging, and clean error handling.

## Project Structure

```
trading_bot/
  bot/
    __init__.py
    client.py           # Binance client wrapper (API layer)
    orders.py            # order placement logic
    validators.py         # input validation
    logging_config.py      # logging setup
  cli.py                  # CLI entry point (command layer)
  logs/
    trading_bot.log        # generated at runtime
  README.md
  requirements.txt
  .env.example
```

The API layer (`client.py`) is fully separated from the command layer
(`cli.py`); `orders.py` sits in between and is the only place that knows
how to turn validated parameters into a logged, structured result. This
makes it straightforward to swap the transport (e.g. direct `requests`
calls instead of `python-binance`) or add a different front end (web UI,
Telegram bot) without touching validation or business logic.

## Setup

1. **Create a Python 3.9+ virtual environment and install dependencies:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Register on Binance Futures Testnet** and generate API credentials:
   - Go to https://testnet.binancefuture.com
   - Log in with a GitHub account
   - Generate an HMAC API key/secret pair from the testnet dashboard

3. **Fund your testnet account** with test USDT — the testnet UI provides
   a faucet for this.

4. **Set your credentials** as environment variables (recommended), or
   pass them directly via CLI flags:

   ```bash
   cp .env.example .env
   # edit .env with your key/secret, then:
   export BINANCE_API_KEY=your_key
   export BINANCE_API_SECRET=your_secret
   ```

## How to Run

**Market order (BUY):**
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

**Limit order (SELL):**
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 60000
```

**Stop-Limit order (bonus order type, BUY):**
```bash
python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 0.01 --price 61000 --stop-price 60900
```

Alternatively, pass credentials inline instead of via environment variables:
```bash
python cli.py --symbol ETHUSDT --side BUY --type MARKET --quantity 0.05 \
  --api-key YOUR_KEY --api-secret YOUR_SECRET
```

Each run prints:
- an **order request summary** (symbol, side, type, quantity, price)
- the **order response** (orderId, status, executedQty, avgPrice)
- a clear **success/failure message**

All requests, responses, and errors are additionally written to
`logs/trading_bot.log` (rotating, 2MB per file, 5 backups kept).

## Order Types Supported

| Type        | Required fields                          |
|-------------|-------------------------------------------|
| MARKET      | symbol, side, quantity                     |
| LIMIT       | symbol, side, quantity, price               |
| STOP_LIMIT  | symbol, side, quantity, price, stop-price (bonus order type) |

## Error Handling

- **Invalid input** (bad symbol format, non-numeric quantity/price, missing
  price for LIMIT orders, etc.) is caught by `validators.py` before any
  network call is made, and reported with a specific message.
- **API errors** (e.g. insufficient margin, invalid precision, closed
  market) raise `BinanceAPIException` / `BinanceOrderException`, which are
  caught in `orders.py`, logged with the Binance error code/message, and
  surfaced to the user without a stack trace.
- **Network failures** (timeouts, connection errors) are caught
  separately and logged distinctly from API-level rejections.
- Any other unexpected exception is caught by a final safety-net handler,
  logged with a full traceback (`logger.exception`) for debugging, while
  the user only sees a concise failure message.

## Assumptions

- Binance Futures Testnet (USDT-M) is used exclusively — no spot or
  mainnet endpoints are touched. The client explicitly pins
  `FUTURES_URL` to `https://testnet.binancefuture.com/fapi` regardless
  of the installed `python-binance` version's default testnet behavior.
- LIMIT and STOP_LIMIT orders use `GTC` (Good-Til-Canceled) time-in-force,
  since the task didn't specify a different policy.
- STOP_LIMIT is implemented as Binance Futures' native `STOP` order type
  (limit price + stop trigger price), chosen as the bonus order type over
  OCO/TWAP/Grid for simplicity and native API support.
- Symbol validation uses a simple `USDT`-suffixed pattern (USDT-M pairs
  only), consistent with the task's BTCUSDT example.
- Quantity/price precision (tick size, lot size) is left to Binance's own
  validation — the bot doesn't hardcode per-symbol precision rules, since
  those are queryable via `exchangeInfo` and out of scope for this task's
  timebox.
- No persistent order storage/database — each CLI invocation is a single,
  self-contained order placement, matching the "simplified trading bot"
  scope.

## Log Files

Two sample log excerpts (one MARKET order, one LIMIT order) are included
in `logs/` as required by the submission — generated from real runs
against Binance Futures Testnet after setting up API credentials as
described above.
