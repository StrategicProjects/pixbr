"""Standalone utility helpers (no network access)."""

from __future__ import annotations

from typing import Iterable, Union

import pandas as pd

from ._odata import parse_year_month  # noqa: F401  (re-exported convenience)


def pix_endpoints() -> pd.DataFrame:
    """Return a DataFrame describing the available BCB PIX API endpoints."""
    return pd.DataFrame(
        [
            ("ChavesPix", "Data", "YYYY-MM-DD", "keys", "PIX keys stock by participant"),
            ("TransacoesPixPorMunicipio", "DataBase", "YYYYMM",
             "transactions_by_municipality", "PIX transactions by municipality"),
            ("EstatisticasTransacoesPix", "Database", "YYYYMM",
             "transaction_stats", "Transaction statistics with breakdowns"),
            ("EstatisticasFraudesPix", "Database", "YYYYMM",
             "fraud_stats", "Fraud statistics (MED)"),
        ],
        columns=["endpoint", "parameter", "param_format", "method", "description"],
    )


_COLUMNS = {
    "keys": [
        ("Data", "string", "Reference date (YYYY-MM-DD, last day of month)"),
        ("ISPB", "string", "8-digit code identifying the financial institution"),
        ("Nome", "string", "Name of the PIX participant (financial institution)"),
        ("NaturezaUsuario", "string", "User type: PF (Individual) or PJ (Legal Entity)"),
        ("TipoChave", "string", "Key type: CPF, CNPJ, Celular, e-mail, or Aleatória"),
        ("qtdChaves", "numeric", "Number of registered keys"),
    ],
    "municipality": [
        ("AnoMes", "integer", "Reference year-month (YYYYMM)"),
        ("Municipio_Ibge", "integer", "IBGE municipality code"),
        ("Municipio", "string", "Municipality name"),
        ("Estado_Ibge", "integer", "IBGE state code"),
        ("Estado", "string", "State name"),
        ("Sigla_Regiao", "string", "Region abbreviation (NE, SE, S, CO, N)"),
        ("Regiao", "string", "Region name"),
        ("VL_PagadorPF", "numeric", "Value paid by individuals (BRL)"),
        ("QT_PagadorPF", "numeric", "Count of transactions with individual payers"),
        ("VL_PagadorPJ", "numeric", "Value paid by legal entities (BRL)"),
        ("QT_PagadorPJ", "numeric", "Count of transactions with legal entity payers"),
        ("VL_RecebedorPF", "numeric", "Value received by individuals (BRL)"),
        ("QT_RecebedorPF", "numeric", "Count of transactions with individual receivers"),
        ("VL_RecebedorPJ", "numeric", "Value received by legal entities (BRL)"),
        ("QT_RecebedorPJ", "numeric", "Count of transactions with legal entity receivers"),
        ("QT_PES_PagadorPF", "numeric", "Distinct individual payers"),
        ("QT_PES_PagadorPJ", "numeric", "Distinct legal entity payers"),
        ("QT_PES_RecebedorPF", "numeric", "Distinct individual receivers"),
        ("QT_PES_RecebedorPJ", "numeric", "Distinct legal entity receivers"),
    ],
    "stats": [
        ("AnoMes", "integer", "Reference year-month (YYYYMM)"),
        ("PAG_PFPJ", "string", "Payer type: PF or PJ"),
        ("REC_PFPJ", "string", "Receiver type: PF or PJ"),
        ("PAG_REGIAO", "string", "Payer region"),
        ("REC_REGIAO", "string", "Receiver region"),
        ("PAG_IDADE", "string", "Payer age group"),
        ("REC_IDADE", "string", "Receiver age group"),
        ("FORMAINICIACAO", "string", "Initiation method (DICT, QRDN, QRES, MANU, INIC)"),
        ("NATUREZA", "string", "Transaction nature (P2P, P2B, B2P, B2B, P2G, G2P)"),
        ("FINALIDADE", "string", "Transaction purpose"),
        ("VALOR", "numeric", "Total transaction value (BRL)"),
        ("QUANTIDADE", "numeric", "Number of transactions"),
    ],
    "fraud": [
        ("AnoMes", "integer", "Reference year-month (YYYYMM)"),
        ("(varies)", "varies", "Fraud statistics columns - query the API for the full schema"),
    ],
}


def pix_columns(endpoint: str = "keys") -> pd.DataFrame:
    """Return column metadata for an endpoint.

    ``endpoint`` is one of ``"keys"``, ``"municipality"``, ``"stats"``, ``"fraud"``.
    """
    if endpoint not in _COLUMNS:
        raise ValueError(
            f"Unknown endpoint {endpoint!r}. Choose one of {list(_COLUMNS)}."
        )
    return pd.DataFrame(_COLUMNS[endpoint], columns=["column", "type", "description"])


def year_month_to_date(year_month: Union[str, Iterable[str]]) -> Union[pd.Timestamp, pd.DatetimeIndex]:
    """Convert ``YYYYMM`` string(s) to date(s) at the first day of the month."""
    if isinstance(year_month, str):
        parse_year_month(year_month)  # validate
        return pd.to_datetime(year_month + "01", format="%Y%m%d")
    values = list(year_month)
    for v in values:
        parse_year_month(v)
    return pd.to_datetime([v + "01" for v in values], format="%Y%m%d")


def format_brl(
    x: Union[float, Iterable[float]],
    prefix: bool = True,
    decimal_mark: str = ",",
    big_mark: str = ".",
) -> Union[str, list[str]]:
    """Format number(s) as Brazilian Real currency (e.g. ``R$ 1.234.567,89``)."""

    def _one(value: float) -> str:
        # Format with US separators first, then swap to BR convention.
        formatted = f"{round(value, 2):,.2f}"
        formatted = formatted.replace(",", "\0").replace(".", decimal_mark).replace("\0", big_mark)
        return f"R$ {formatted}" if prefix else formatted

    if isinstance(x, (int, float)):
        return _one(float(x))
    return [_one(float(v)) for v in x]
