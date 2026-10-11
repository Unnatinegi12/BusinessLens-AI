import pytest


def calculate_revenue(quantity, unit_price, discount, status):
    if status == "Cancelled":
        return 0
    return quantity * unit_price * (1 - discount)


def test_revenue_without_discount():
    assert calculate_revenue(2, 100, 0, "Delivered") == 200


def test_revenue_with_discount():
    assert calculate_revenue(2, 100, 0.10, "Delivered") == pytest.approx(180)


def test_cancelled_order():
    assert calculate_revenue(2, 100, 0, "Cancelled") == 0


def test_full_discount():
    assert calculate_revenue(2, 100, 1.0, "Delivered") == 0


def test_zero_quantity():
    assert calculate_revenue(0, 100, 0.10, "Delivered") == 0
