"""URL-building tests, validated against the behaviour of pixr::pix_request."""

import warnings

import pytest

from pixbr import _odata


BASE = _odata.BASE_URL


def test_keys_url_basic():
    url = _odata.build_url("ChavesPix", {"Data": "2025-12-01"}, top=10)
    assert url == (
        f"{BASE}/ChavesPix(Data=@Data)"
        "?$format=json&@Data='2025-12-01'&$top=10"
    )


def test_stats_url_with_filter_select_orderby():
    url = _odata.build_url(
        "EstatisticasTransacoesPix",
        {"Database": "202509"},
        filter="NATUREZA eq 'P2P'",
        select=["NATUREZA", "VALOR", "QUANTIDADE"],
        orderby="VALOR desc",
        top=100,
    )
    # Spaces become %20; nothing else is percent-encoded.
    assert url == (
        f"{BASE}/EstatisticasTransacoesPix(Database=@Database)"
        "?$format=json&@Database='202509'"
        "&$filter=NATUREZA%20eq%20'P2P'"
        "&$select=NATUREZA,VALOR,QUANTIDADE"
        "&$orderby=VALOR%20desc"
        "&$top=100"
    )


def test_municipality_uses_capital_b_param():
    url = _odata.build_url("TransacoesPixPorMunicipio", {"DataBase": "202512"})
    assert "TransacoesPixPorMunicipio(DataBase=@DataBase)" in url
    assert "@DataBase='202512'" in url


def test_no_params_no_function_call():
    url = _odata.build_url("SomeEndpoint")
    assert url == f"{BASE}/SomeEndpoint?$format=json"


def test_filter_whitespace_after_comma_and_paren_collapsed():
    url = _odata.build_url(
        "X", {"A": "1"}, filter="f(a, b) and g( c)"
    )
    # "f(a, b)" -> "f(a,b)" and "g( c)" -> "g(c)" before space->%20.
    assert "$filter=f(a,b)%20and%20g(c)" in url


def test_skip_warns_and_is_ignored():
    with pytest.warns(UserWarning, match="skip"):
        url = _odata.build_url("X", {"A": "1"}, skip=50)
    assert "skip" not in url.lower()


def test_numeric_param_not_quoted():
    url = _odata.build_url("X", {"N": 202509})
    assert "@N=202509" in url
    assert "@N='202509'" not in url


# -- parsing helpers ---------------------------------------------------


def test_parse_year_month_valid():
    assert _odata.parse_year_month("202312") == "202312"
    assert _odata.parse_year_month(202312) == "202312"


def test_parse_year_month_invalid():
    with pytest.raises(ValueError):
        _odata.parse_year_month("2023")


def test_parse_date_param():
    assert _odata.parse_date_param("2025-12-01") == "2025-12-01"
    with pytest.raises(ValueError):
        _odata.parse_date_param("2025/12/01")


def test_validate_columns_drops_unknown():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        kept = _odata.validate_columns(["A", "Z"], ["A", "B"])
    assert kept == ["A"]


def test_validate_columns_all_invalid_returns_none():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert _odata.validate_columns(["Z"], ["A", "B"]) is None


def test_format_orderby_dash_prefix():
    assert _odata.format_orderby("-VALOR") == "VALOR desc"
    assert _odata.format_orderby("VALOR") == "VALOR asc"
    assert _odata.format_orderby("VALOR desc") == "VALOR desc"
