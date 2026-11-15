from datetime import datetime
from decimal import Decimal, InvalidOperation


def dt(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def date(value):
    parsed = dt(value)
    return parsed.date() if parsed else None


def money(value):
    try:
        return Decimal(str(value or 0))
    except InvalidOperation:
        return Decimal("0")


def boolean(value):
    return str(value).strip().lower() in {"1", "true", "sim", "yes"}
