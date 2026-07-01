#!/usr/bin/env python3
"""
CLI entry point for the Binance Futures Testnet trading bot.

Usage examples:
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
    python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 60000
    python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 0.01 --price 61000 --stop-price 60900

API credentials are read from environment variables BINANCE_API_KEY /
BINANCE_API_SECRET (see README.md), or from --api-key / --api-secret.
"""

import argparse
import os
import sys

from binance.exceptions import BinanceAPIException, BinanceRequestException

from bot.logging_config import setup_logging
from bot.validators import validate_order_params, ValidationError
from bot.client import BinanceFuturesTestnetClient
from bot.orders import place_order

logger = setup_logging()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Place MARKET / LIMIT / STOP_LIMIT orders on Binance Futures Testnet (USDT-M)."
    )
    parser.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, choices=["BUY", "SELL", "buy", "sell"], help="Order side")
    parser.add_argument(
        "--type", dest="order_type", required=True,
        choices=["MARKET", "LIMIT", "STOP_LIMIT", "market", "limit", "stop_limit"],
        help="Order type",
    )
    parser.add_argument("--quantity", required=True, help="Order quantity")
    parser.add_argument("--price", default=None, help="Limit price (required for LIMIT / STOP_LIMIT)")
    parser.add_argument("--stop-price", dest="stop_price", default=None, help="Stop price (required for STOP_LIMIT)")
    parser.add_argument("--api-key", default=os.environ.get("BINANCE_API_KEY"), help="Binance Testnet API key")
    parser.add_argument("--api-secret", default=os.environ.get("BINANCE_API_SECRET"), help="Binance Testnet API secret")
    return parser


def print_summary(title: str, data: dict):
    print(f"\n{title}")
    print("-" * len(title))
    for key, value in data.items():
        if value is not None:
            print(f"  {key}: {value}")


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        params = validate_order_params(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
    except ValidationError as exc:
        logger.error("Input validation failed: %s", exc)
        print(f"\n[FAILED] Invalid input: {exc}")
        sys.exit(1)

    print_summary("Order Request Summary", {
        "Symbol": params["symbol"],
        "Side": params["side"],
        "Type": params["order_type"],
        "Quantity": params["quantity"],
        "Price": params["price"],
        "Stop Price": params["stop_price"],
    })

    try:
        client = BinanceFuturesTestnetClient(args.api_key, args.api_secret)
    except ValueError as exc:
        logger.error("Client initialization failed: %s", exc)
        print(f"\n[FAILED] {exc}")
        sys.exit(1)
    except (BinanceAPIException, BinanceRequestException) as exc:
        logger.error("Could not reach Binance Futures Testnet: %s", exc)
        print(f"\n[FAILED] Could not reach Binance Futures Testnet: {exc}")
        sys.exit(1)
    except (ConnectionError, TimeoutError) as exc:
        logger.error("Network error while connecting to Binance Futures Testnet: %s", exc)
        print(f"\n[FAILED] Network error: {exc}")
        sys.exit(1)

    result = place_order(client, params)

    if result.success:
        r = result.response
        print_summary("Order Response", {
            "Order ID": r.get("orderId"),
            "Status": r.get("status"),
            "Executed Qty": r.get("executedQty"),
            "Avg Price": r.get("avgPrice"),
        })
        print("\n[SUCCESS] Order placed successfully.\n")
    else:
        print(f"\n[FAILED] {result.error}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
