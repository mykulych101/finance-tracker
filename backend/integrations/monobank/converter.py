from decimal import Decimal

CURRENCY_CODE_MAP = {"USD": 840, "EUR": 978, "UAH": 980}
UAH_CODE = 980


def _to_uah(amount: Decimal, from_currency: str, rates: list[dict]) -> Decimal:
    from_code = CURRENCY_CODE_MAP[from_currency]
    rate = next(
        (r for r in rates if r["currencyCodeA"] == from_code and r["currencyCodeB"] == UAH_CODE),
        None,
    )
    if rate is None:
        msg = f"No rate found for {from_currency} → UAH"
        raise ValueError(msg)
    return amount * Decimal(str(rate["rateBuy"]))  # bank buys from you → what you'd receive


def _from_uah(amount: Decimal, to_currency: str, rates: list[dict]) -> Decimal:
    to_code = CURRENCY_CODE_MAP[to_currency]
    rate = next(
        (r for r in rates if r["currencyCodeA"] == to_code and r["currencyCodeB"] == UAH_CODE),
        None,
    )
    if rate is None:
        msg = f"No rate found for UAH → {to_currency}"
        raise ValueError(msg)
    return amount / Decimal(str(rate["rateSell"]))  # bank sells to you → what you'd pay per unit


def convert_amount(amount: Decimal, from_currency: str, to_currency: str, rates: list[dict]) -> Decimal:
    if from_currency == to_currency:
        return amount
    if to_currency == "UAH":
        return _to_uah(amount, from_currency, rates)
    if from_currency == "UAH":
        return _from_uah(amount, to_currency, rates)
    # Cross-rate via UAH pivot (e.g. USD → UAH → EUR)
    return _from_uah(_to_uah(amount, from_currency, rates), to_currency, rates)
