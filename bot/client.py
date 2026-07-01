"""
Thin wrapper around python-binance's Client, scoped to Binance Futures
Testnet (USDT-M). Keeping this isolated from orders.py/cli.py means the
underlying HTTP/SDK layer can be swapped (e.g. for direct REST calls)
without touching business logic.
"""

import logging
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException, BinanceRequestException

logger = logging.getLogger("trading_bot")

FUTURES_TESTNET_BASE_URL = "https://testnet.binancefuture.com"


class BinanceFuturesTestnetClient:
    """Wraps a python-binance Client configured for Futures Testnet."""

    def __init__(self, api_key: str, api_secret: str):
        if not api_key or not api_secret:
            raise ValueError("API key and secret must be provided (see README setup).")

        # python-binance's `testnet=True` flag points both spot and
        # futures endpoints at their respective testnets. We additionally
        # pin FUTURES_URL explicitly so behavior is correct even on
        # library versions where the flag only affects spot.
        self.client = Client(api_key, api_secret, testnet=True)
        self.client.FUTURES_URL = FUTURES_TESTNET_BASE_URL + "/fapi"
        logger.debug("Initialized Binance Futures Testnet client at %s", FUTURES_TESTNET_BASE_URL)

    def place_order(self, symbol: str, side: str, order_type: str, quantity: float,
                     price: float = None, stop_price: float = None) -> dict:
        """
        Place an order on Futures Testnet. Raises BinanceAPIException /
        BinanceOrderException / BinanceRequestException on failure, which
        the caller (orders.py) is expected to catch and log.
        """
        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type if order_type != "STOP_LIMIT" else "STOP",
            "quantity": quantity,
        }

        if order_type == "LIMIT":
            params["timeInForce"] = "GTC"
            params["price"] = price
        elif order_type == "STOP_LIMIT":
            params["timeInForce"] = "GTC"
            params["price"] = price
            params["stopPrice"] = stop_price

        logger.debug("Sending futures_create_order request: %s", params)
        response = self.client.futures_create_order(**params)
        logger.debug("Received futures_create_order response: %s", response)
        return response

    def get_order_status(self, symbol: str, order_id: int) -> dict:
        """Fetch the latest status of a previously placed order."""
        logger.debug("Fetching order status for symbol=%s order_id=%s", symbol, order_id)
        response = self.client.futures_get_order(symbol=symbol, orderId=order_id)
        logger.debug("Order status response: %s", response)
        return response
