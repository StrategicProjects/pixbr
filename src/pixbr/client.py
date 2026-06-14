"""HTTP client for the BCB PIX Open Data API."""

from __future__ import annotations

import logging
from typing import Mapping, Optional, Sequence

import httpx
import pandas as pd

from . import _odata
from ._odata import ParamValue

logger = logging.getLogger("pixbr")

# Endpoint metadata: endpoint name -> (param name, param format).
ENDPOINTS = {
    "ChavesPix": ("Data", "YYYY-MM-DD"),
    "TransacoesPixPorMunicipio": ("DataBase", "YYYYMM"),
    "EstatisticasTransacoesPix": ("Database", "YYYYMM"),
    "EstatisticasFraudesPix": ("Database", "YYYYMM"),
}

_USER_AGENT = "pixbr Python package (https://github.com/StrategicProjects/pixbr)"


class PixApiError(RuntimeError):
    """Raised when the BCB PIX API returns an error or cannot be reached."""


class PixClient:
    """Client for the Brazilian Central Bank PIX Open Data API.

    Parameters
    ----------
    timeout:
        Request timeout in seconds (default 120). The BCB API can be slow for
        large queries, so a generous timeout is recommended.
    max_retries:
        Number of retry attempts on transport errors (default 3).
    verbose:
        If True (default), log progress messages at INFO level.

    Examples
    --------
    >>> client = PixClient()
    >>> df = client.keys(date="2025-12-01", top=100)  # doctest: +SKIP
    """

    def __init__(
        self,
        timeout: float = _odata.DEFAULT_TIMEOUT,
        max_retries: int = 3,
        verbose: bool = True,
    ) -> None:
        self.timeout = timeout
        self.verbose = verbose
        transport = httpx.HTTPTransport(retries=max_retries)
        self._http = httpx.Client(
            timeout=timeout,
            transport=transport,
            headers={
                "Accept": "application/json;odata.metadata=minimal",
                "User-Agent": _USER_AGENT,
            },
        )

    # -- context manager / lifecycle ------------------------------------

    def __enter__(self) -> "PixClient":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def close(self) -> None:
        self._http.close()

    # -- low-level ------------------------------------------------------

    def build_url(
        self,
        endpoint: str,
        params: Optional[Mapping[str, ParamValue]] = None,
        *,
        fmt: str = "json",
        filter: Optional[str] = None,
        select: Optional[Sequence[str]] = None,
        orderby: Optional[str] = None,
        top: Optional[int] = None,
        skip: Optional[int] = None,
    ) -> str:
        """Build (without sending) the URL for a request. Useful for debugging."""
        return _odata.build_url(
            endpoint,
            params,
            fmt=fmt,
            filter=filter,
            select=select,
            orderby=orderby,
            top=top,
            skip=skip,
        )

    def query(
        self,
        endpoint: str,
        params: Optional[Mapping[str, ParamValue]] = None,
        *,
        filter: Optional[str] = None,
        select: Optional[Sequence[str]] = None,
        orderby: Optional[str] = None,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        verbose: Optional[bool] = None,
    ) -> pd.DataFrame:
        """Low-level call to any PIX endpoint; returns a DataFrame.

        This is the Python equivalent of ``pixr::pix_query``.
        """
        url = self.build_url(
            endpoint,
            params,
            filter=filter,
            select=select,
            orderby=orderby,
            top=top,
            skip=skip,
        )
        return self._perform(url, verbose=verbose)

    def _perform(self, url: str, verbose: Optional[bool] = None) -> pd.DataFrame:
        verbose = self.verbose if verbose is None else verbose
        if verbose:
            logger.info("URL: %s", url)

        try:
            resp = self._http.get(url)
        except httpx.HTTPError as exc:
            raise PixApiError(
                f"Connection error to BCB PIX API. Check your internet connection; "
                f"the API may be temporarily unavailable. URL: {url}"
            ) from exc

        if resp.status_code != 200:
            body = resp.text[:500]
            raise PixApiError(
                f"API request failed with status {resp.status_code} "
                f"({resp.reason_phrase}). URL: {resp.url}. Response: {body}"
            )

        try:
            body = resp.json()
        except ValueError as exc:
            raise PixApiError(
                f"Failed to parse JSON response. Raw response: {resp.text[:500]}"
            ) from exc

        # OData responses wrap rows in a top-level 'value' field.
        data = body.get("value", body) if isinstance(body, dict) else body

        if not data:
            if verbose:
                logger.info("No data returned from API")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        if verbose:
            logger.info("Retrieved %d record(s)", len(df))
        return df

    # -- typed endpoint accessors --------------------------------------

    def keys(
        self,
        date: str,
        *,
        filter: Optional[str] = None,
        columns: Optional[Sequence[str]] = None,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        orderby: Optional[str] = None,
        verbose: Optional[bool] = None,
    ) -> pd.DataFrame:
        """PIX keys stock by participant (ChavesPix endpoint).

        ``date`` is required, in YYYY-MM-DD form. The API returns data for the
        last day of the month containing the given date.
        """
        valid = ["Data", "ISPB", "Nome", "NaturezaUsuario", "TipoChave", "qtdChaves"]
        columns = _odata.validate_columns(columns, valid)
        df = self.query(
            "ChavesPix",
            {"Data": _odata.parse_date_param(date)},
            filter=filter,
            select=columns,
            orderby=orderby,
            top=top,
            skip=skip,
            verbose=verbose,
        )
        return _coerce_numeric(df, ["qtdChaves"])

    def transaction_stats(
        self,
        database: str,
        *,
        filter: Optional[str] = None,
        columns: Optional[Sequence[str]] = None,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        orderby: Optional[str] = None,
        verbose: Optional[bool] = None,
    ) -> pd.DataFrame:
        """PIX transaction statistics (EstatisticasTransacoesPix endpoint).

        ``database`` is required, in YYYYMM form.
        """
        valid = [
            "AnoMes", "PAG_PFPJ", "REC_PFPJ", "PAG_REGIAO", "REC_REGIAO",
            "PAG_IDADE", "REC_IDADE", "FORMAINICIACAO", "NATUREZA",
            "FINALIDADE", "VALOR", "QUANTIDADE",
        ]
        columns = _odata.validate_columns(columns, valid)
        df = self.query(
            "EstatisticasTransacoesPix",
            {"Database": _odata.parse_year_month(database)},
            filter=filter,
            select=columns,
            orderby=orderby,
            top=top,
            skip=skip,
            verbose=verbose,
        )
        return _coerce_numeric(df, ["AnoMes", "VALOR", "QUANTIDADE"])

    def transactions_by_municipality(
        self,
        database: str,
        *,
        filter: Optional[str] = None,
        columns: Optional[Sequence[str]] = None,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        orderby: Optional[str] = None,
        verbose: Optional[bool] = None,
    ) -> pd.DataFrame:
        """PIX transactions by municipality (TransacoesPixPorMunicipio endpoint).

        ``database`` is required, in YYYYMM form. Note this endpoint uses the
        ``DataBase`` parameter (capital B).
        """
        valid = [
            "AnoMes", "Municipio_Ibge", "Municipio", "Estado_Ibge", "Estado",
            "Sigla_Regiao", "Regiao",
            "VL_PagadorPF", "QT_PagadorPF", "VL_PagadorPJ", "QT_PagadorPJ",
            "VL_RecebedorPF", "QT_RecebedorPF", "VL_RecebedorPJ", "QT_RecebedorPJ",
            "QT_PES_PagadorPF", "QT_PES_PagadorPJ",
            "QT_PES_RecebedorPF", "QT_PES_RecebedorPJ",
        ]
        columns = _odata.validate_columns(columns, valid)
        df = self.query(
            "TransacoesPixPorMunicipio",
            {"DataBase": _odata.parse_year_month(database)},
            filter=filter,
            select=columns,
            orderby=orderby,
            top=top,
            skip=skip,
            verbose=verbose,
        )
        numeric = [c for c in valid if c not in ("Municipio", "Estado", "Sigla_Regiao", "Regiao")]
        return _coerce_numeric(df, numeric)

    def fraud_stats(
        self,
        database: str,
        *,
        filter: Optional[str] = None,
        columns: Optional[Sequence[str]] = None,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        orderby: Optional[str] = None,
        verbose: Optional[bool] = None,
    ) -> pd.DataFrame:
        """PIX fraud statistics / MED (EstatisticasFraudesPix endpoint).

        ``database`` is required, in YYYYMM form. The exact schema varies, so
        columns are not validated; numeric-looking columns are coerced.
        """
        df = self.query(
            "EstatisticasFraudesPix",
            {"Database": _odata.parse_year_month(database)},
            filter=filter,
            select=columns,
            orderby=orderby,
            top=top,
            skip=skip,
            verbose=verbose,
        )
        if not df.empty:
            patterns = ("QT_", "VL_", "QUANTIDADE", "VALOR", "ANOMES")
            numeric = [c for c in df.columns if any(p in c.upper() for p in patterns)]
            df = _coerce_numeric(df, numeric)
        return df

    def ping(self) -> pd.DataFrame:
        """Test connectivity to all four endpoints with a single-record request."""
        probes = {
            "ChavesPix": {"Data": "2025-01-01"},
            "TransacoesPixPorMunicipio": {"DataBase": "202501"},
            "EstatisticasTransacoesPix": {"Database": "202501"},
            "EstatisticasFraudesPix": {"Database": "202501"},
        }
        rows = []
        for endpoint, params in probes.items():
            url = self.build_url(endpoint, params, top=1)
            try:
                resp = self._http.get(url)
                status = "OK" if resp.status_code == 200 else f"HTTP {resp.status_code}"
            except httpx.HTTPError as exc:
                status = str(exc)
            rows.append({"endpoint": endpoint, "status": status})
        return pd.DataFrame(rows)


def _coerce_numeric(df: pd.DataFrame, columns: Sequence[str]) -> pd.DataFrame:
    if df.empty:
        return df
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df
