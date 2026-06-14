import pandas as pd

from pixbr import format_brl, pix_columns, pix_endpoints, year_month_to_date


def test_format_brl_scalar():
    assert format_brl(1234567.89) == "R$ 1.234.567,89"
    assert format_brl(1000) == "R$ 1.000,00"


def test_format_brl_no_prefix():
    assert format_brl(1234.5, prefix=False) == "1.234,50"


def test_format_brl_vector():
    assert format_brl([1000, 2000]) == ["R$ 1.000,00", "R$ 2.000,00"]


def test_year_month_to_date_scalar():
    ts = year_month_to_date("202312")
    assert ts == pd.Timestamp("2023-12-01")


def test_year_month_to_date_vector():
    idx = year_month_to_date(["202301", "202302"])
    assert list(idx) == [pd.Timestamp("2023-01-01"), pd.Timestamp("2023-02-01")]


def test_pix_endpoints_shape():
    df = pix_endpoints()
    assert len(df) == 4
    assert set(["endpoint", "parameter", "method"]).issubset(df.columns)


def test_pix_columns_keys():
    df = pix_columns("keys")
    assert "qtdChaves" in df["column"].values
