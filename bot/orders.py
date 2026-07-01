"""
Order placement logic: takes validated parameters, talks to the client
layer, logs the full request/response/error trail, and returns a
structured result the CLI layer can print.
"""

import logging
from dataclasses import dataclass, field
from typing import Optional

from binance.exceptions import BinanceAPIException, BinanceOrderException, BinanceRequestException

from bot.client import BinanceFuturesTestnetClient

logger = logging.getLogger("trading_bot")


@dataclass
class OrderResult:
    success: bool
    request_summary: dict
    response: Optional[dict] = None
    error: Optional[str] = None


def place_order(client: BinanceFuturesTestnetClient, params: dict) -> OrderResult:
    """
    Place an order using already-validated params (see validators.py).
    Logs the request, the raw response (or error), and returns an
    OrderResult for the CLI layer to display.
    """
    request_summary = {
        "symbol": params["symbol"],
        "side": params["side"],
        "type": params["order_type"],
        "quantity": params["quantity"],
        "price": params.get("price"),
        "stop_price": params.get("stop_price"),
    }

    logger.info("Order request: %s", request_summary)

    try:
        response = client.place_order(
            symbol=params["symbol"],
            side=params["side"],
            order_type=params["order_type"],
            quantity=params["quantity"],
            price=params.get("price"),
            stop_price=params.get("stop_price"),
        )
        logger.info(
            "Order accepted: orderId=%s status=%s executedQty=%s avgPrice=%s",
            response.get("orderId"),
            response.get("status"),
            response.get("executedQty"),
            response.get("avgPrice"),
        )
        return OrderResult(success=True, request_summary=request_summary, response=response)

    except (BinanceAPIException, BinanceOrderException) as exc:
        # Binance rejected the request (bad symbol, insufficient margin,
        # invalid price/quantity precision, etc.)
        error_msg = f"Binance API error (code={getattr(exc, 'code', '?')}): {exc.message if hasattr(exc, 'message') else exc}"
        logger.error("Order rejected: %s | request=%s", error_msg, request_summary)
        return OrderResult(success=False, request_summary=request_summary, error=error_msg)

    except BinanceRequestException as exc:
        # Malformed request never reached Binance's matching engine
        error_msg = f"Malformed request: {exc}"
        logger.error("Order request malformed: %s | request=%s", error_msg, request_summary)
        return OrderResult(success=False, request_summary=request_summary, error=error_msg)

    except (ConnectionError, TimeoutError) as exc:
        error_msg = f"Network error: {exc}"
        logger.error("Network failure while placing order: %s | request=%s", error_msg, request_summary)
        return OrderResult(success=False, request_summary=request_summary, error=error_msg)

    except Exception as exc:  # noqa: BLE001 - last-resort safety net, still logged with context
        error_msg = f"Unexpected error: {exc}"
        logger.exception("Unexpected error placing order | request=%s", request_summary)
        return OrderResult(success=False, request_summary=request_summary, error=error_msg)
