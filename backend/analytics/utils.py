import bisect
import calendar
from datetime import date as date_type, timedelta
from decimal import ROUND_HALF_UP, Decimal

from accounts.constants import AccountCategory, AccountType
from integrations.monobank.converter import convert_amount


def generate_buckets(date_after, date_before, period):
    """Return the list of bucket end-dates between date_after and date_before for the given period."""
    buckets = []
    if period == "daily":
        current = date_after
        while current <= date_before:
            buckets.append(current)
            current += timedelta(days=1)
    elif period == "weekly":
        days_to_sunday = (6 - date_after.weekday()) % 7
        current = date_after + timedelta(days=days_to_sunday or 7)
        while current <= date_before:
            buckets.append(current)
            current += timedelta(weeks=1)
    elif period == "monthly":
        year, month = date_after.year, date_after.month
        while True:
            last_day = calendar.monthrange(year, month)[1]
            end = date_type(year, month, last_day)
            buckets.append(min(end, date_before))
            if end >= date_before:
                break
            month += 1
            if month > 12:  # noqa: PLR2004
                month, year = 1, year + 1
    return buckets


def aggregate_net_worth(accounts, convert_to=None, rates=None):
    """Return (assets_total, liabilities_total) for a list of accounts with latest_balance annotated."""
    rates = rates or []
    assets = Decimal(0)
    liabilities = Decimal(0)
    for account in accounts:
        balance = Decimal(str(account.latest_balance or 0))
        if convert_to:
            balance = convert_amount(balance, account.currency, convert_to, rates)
        if account.type == AccountType.ASSET:
            assets += balance
        elif account.type == AccountType.LIABILITY:
            if account.category == AccountCategory.CREDIT_CARD:
                limit = Decimal(str(account.credit_limit or 0))
                if convert_to:
                    limit = convert_amount(limit, account.currency, convert_to, rates)
                liabilities += limit - balance
            else:
                liabilities += balance
    quantize = Decimal("0.01")
    return assets.quantize(quantize, rounding=ROUND_HALF_UP), liabilities.quantize(quantize, rounding=ROUND_HALF_UP)


def aggregate_net_worth_history(accounts, records_by_account, buckets, convert_to=None, rates=None):
    """Compute net worth at each bucket date.

    `records_by_account` maps an account id to its [(date, amount), ...] sorted by (date, created_at) asc.
    For each bucket the latest balance on or before that date is carried forward per account, then reused
    through aggregate_net_worth.
    """
    indexed = {
        account_id: ([d for d, _ in records], [a for _, a in records])
        for account_id, records in records_by_account.items()
    }
    history = []
    for bucket_date in buckets:
        for account in accounts:
            dates, amounts = indexed.get(account.id, ((), ()))
            idx = bisect.bisect_right(dates, bucket_date)
            account.latest_balance = amounts[idx - 1] if idx else None
        assets, liabilities = aggregate_net_worth(accounts, convert_to, rates)
        history.append(
            {
                "date": bucket_date,
                "assets": assets,
                "liabilities": liabilities,
                "net_worth": assets - liabilities,
            }
        )
    return history
