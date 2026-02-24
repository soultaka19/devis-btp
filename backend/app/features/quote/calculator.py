from dataclasses import dataclass

VALID_VAT_RATES = {5.5, 10.0, 20.0}


@dataclass
class LineTotal:
    total_ht: float
    vat_amount: float
    total_ttc: float


@dataclass
class QuoteTotals:
    subtotal_ht: float
    total_vat: float
    total_ttc: float
    vat_breakdown: dict[float, float]  # rate -> vat_amount


def calc_line_total(quantity: float, unit_price: float, vat_rate: float = 20.0) -> LineTotal:
    total_ht = round(quantity * unit_price, 2)
    vat_amount = round(total_ht * vat_rate / 100, 2)
    total_ttc = round(total_ht + vat_amount, 2)
    return LineTotal(total_ht=total_ht, vat_amount=vat_amount, total_ttc=total_ttc)


def calc_vat(amount_ht: float, vat_rate: float = 20.0) -> float:
    return round(amount_ht * vat_rate / 100, 2)


def calc_quote_totals(
    lines: list[dict],
) -> QuoteTotals:
    """Calculate totals from a list of line items.

    Each dict must have: quantity, unit_price, vat_rate
    """
    subtotal_ht = 0.0
    total_vat = 0.0
    vat_breakdown: dict[float, float] = {}

    for line in lines:
        lt = calc_line_total(line["quantity"], line["unit_price"], line["vat_rate"])
        subtotal_ht += lt.total_ht
        total_vat += lt.vat_amount
        vat_breakdown[line["vat_rate"]] = vat_breakdown.get(line["vat_rate"], 0.0) + lt.vat_amount

    subtotal_ht = round(subtotal_ht, 2)
    total_vat = round(total_vat, 2)
    total_ttc = round(subtotal_ht + total_vat, 2)

    return QuoteTotals(
        subtotal_ht=subtotal_ht,
        total_vat=total_vat,
        total_ttc=total_ttc,
        vat_breakdown={k: round(v, 2) for k, v in vat_breakdown.items()},
    )
