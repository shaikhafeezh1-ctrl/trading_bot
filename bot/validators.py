"""
Input validation for order parameters coming from the CLI.

Keeping this separate from cli.py and orders.py means the same
validation logic can be reused if a UI or API layer is added later.
"""

import re

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_LIMIT"}

# Reasonable sanity pattern for Binance Futures USDT-M symbols, e.g. BTCUSDT, ETHUSDT
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{2,15}USDT$")


class ValidationError(Exception):
    """Raised when CLI-supplied order parameters fail validation."""


def validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not SYMBOL_PATTERN.match(symbol):
        raise ValidationError(
            f"Invalid symbol '{symbol}'. Expected a USDT-M pair like 'BTCUSDT'."
        )
    return symbol


def validate_side(side: str) -> str:
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValidationError(f"Invalid side '{side}'. Must be one of {VALID_SIDES}.")
    return side


def validate_order_type(order_type: str) -> str:
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. Must be one of {VALID_ORDER_TYPES}."
        )
    return order_type


def validate_quantity(quantity: float) -> float:
    try:
        quantity = float(quantity)
    except (TypeError, ValueError):
        raise ValidationError(f"Quantity must be numeric, got '{quantity}'.")
    if quantity <= 0:
        raise ValidationError(f"Quantity must be > 0, got {quantity}.")
    return quantity


def validate_price(price, order_type: str):
    """Price is required for LIMIT and STOP_LIMIT orders, disallowed for MARKET."""
    if order_type == "MARKET":
        return None
    if price is None:
        raise ValidationError(f"Price is required for {order_type} orders.")
    try:
        price = float(price)
    except (TypeError, ValueError):
        raise ValidationError(f"Price must be numeric, got '{price}'.")
    if price <= 0:
        raise ValidationError(f"Price must be > 0, got {price}.")
    return price


def validate_stop_price(stop_price, order_type: str):
    """Stop price is required only for STOP_LIMIT orders."""
    if order_type != "STOP_LIMIT":
        return None
    if stop_price is None:
        raise ValidationError("Stop price is required for STOP_LIMIT orders.")
    try:
        stop_price = float(stop_price)
    except (TypeError, ValueError):
        raise ValidationError(f"Stop price must be numeric, got '{stop_price}'.")
    if stop_price <= 0:
        raise ValidationError(f"Stop price must be > 0, got {stop_price}.")
    return stop_price


def validate_order_params(symbol, side, order_type, quantity, price=None, stop_price=None):
    """Run all validations and return a clean, normalized dict of params."""
    symbol = validate_symbol(symbol)
    side = validate_side(side)
    order_type = validate_order_type(order_type)
    quantity = validate_quantity(quantity)
    price = validate_price(price, order_type)
    stop_price = validate_stop_price(stop_price, order_type)

    return {
        "symbol": symbol,
        "side": side,
        "order_type": order_type,
        "quantity": quantity,
        "price": price,
        "stop_price": stop_price,
    }
