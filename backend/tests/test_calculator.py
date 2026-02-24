from app.features.quote.calculator import calc_line_total, calc_quote_totals, calc_vat


def test_calc_line_total_basic():
    result = calc_line_total(2, 100.0, 20.0)
    assert result.total_ht == 200.0
    assert result.vat_amount == 40.0
    assert result.total_ttc == 240.0


def test_calc_line_total_renovation_vat():
    result = calc_line_total(10, 50.0, 10.0)
    assert result.total_ht == 500.0
    assert result.vat_amount == 50.0
    assert result.total_ttc == 550.0


def test_calc_line_total_reduced_vat():
    result = calc_line_total(1, 1000.0, 5.5)
    assert result.total_ht == 1000.0
    assert result.vat_amount == 55.0
    assert result.total_ttc == 1055.0


def test_calc_line_total_zero_quantity():
    result = calc_line_total(0, 100.0, 20.0)
    assert result.total_ht == 0.0
    assert result.vat_amount == 0.0
    assert result.total_ttc == 0.0


def test_calc_line_total_decimal_quantities():
    result = calc_line_total(2.5, 40.0, 20.0)
    assert result.total_ht == 100.0
    assert result.vat_amount == 20.0
    assert result.total_ttc == 120.0


def test_calc_vat():
    assert calc_vat(100.0, 20.0) == 20.0
    assert calc_vat(100.0, 10.0) == 10.0
    assert calc_vat(100.0, 5.5) == 5.5
    assert calc_vat(0.0, 20.0) == 0.0


def test_calc_quote_totals_single_line():
    lines = [{"quantity": 3, "unit_price": 45.0, "vat_rate": 10.0}]
    result = calc_quote_totals(lines)
    assert result.subtotal_ht == 135.0
    assert result.total_vat == 13.5
    assert result.total_ttc == 148.5
    assert result.vat_breakdown == {10.0: 13.5}


def test_calc_quote_totals_mixed_vat():
    lines = [
        {"quantity": 1, "unit_price": 100.0, "vat_rate": 20.0},
        {"quantity": 2, "unit_price": 50.0, "vat_rate": 10.0},
        {"quantity": 1, "unit_price": 200.0, "vat_rate": 5.5},
    ]
    result = calc_quote_totals(lines)
    assert result.subtotal_ht == 400.0
    assert result.vat_breakdown[20.0] == 20.0
    assert result.vat_breakdown[10.0] == 10.0
    assert result.vat_breakdown[5.5] == 11.0
    assert result.total_vat == 41.0
    assert result.total_ttc == 441.0


def test_calc_quote_totals_empty():
    result = calc_quote_totals([])
    assert result.subtotal_ht == 0.0
    assert result.total_vat == 0.0
    assert result.total_ttc == 0.0
    assert result.vat_breakdown == {}


def test_calc_quote_totals_rounding():
    lines = [{"quantity": 3, "unit_price": 33.33, "vat_rate": 20.0}]
    result = calc_quote_totals(lines)
    assert result.subtotal_ht == 99.99
    assert result.total_vat == 20.0
    assert result.total_ttc == 119.99
