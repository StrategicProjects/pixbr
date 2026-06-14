"""URL building and parameter helpers for the BCB PIX Open Data (OData) API.

The BCB Olinda API uses a non-standard OData syntax where endpoint parameters
are passed as function arguments in the URL path *and* repeated as named query
parameters, e.g.::

    ChavesPix(Data=@Data)?$format=json&@Data='2025-12-01'&$top=10

These helpers reproduce the exact URL construction used by the R package
``pixr`` (which deliberately avoids standard percent-encoding, encoding only
spaces as ``%20``). They are pure functions so they can be unit-tested without
hitting the network.
"""

from __future__ import annotations

import re
import warnings
from datetime import date, datetime
from typing import Mapping, Optional, Sequence, Union

BASE_URL = "https://olinda.bcb.gov.br/olinda/servico/Pix_DadosAbertos/versao/v1/odata"
DEFAULT_TIMEOUT = 120

ParamValue = Union[str, int, float]


def build_url(
    endpoint: str,
    params: Optional[Mapping[str, ParamValue]] = None,
    *,
    fmt: str = "json",
    filter: Optional[str] = None,
    select: Optional[Sequence[str]] = None,
    orderby: Optional[str] = None,
    top: Optional[int] = None,
    skip: Optional[int] = None,
    base_url: str = BASE_URL,
) -> str:
    """Build a full request URL for a BCB PIX OData endpoint.

    Mirrors ``pixr::pix_request`` URL construction exactly.
    """
    # Endpoint path, with function-style parameter declaration.
    if params:
        func_params = ",".join(f"{name}=@{name}" for name in params)
        endpoint_url = f"{base_url}/{endpoint}({func_params})"
    else:
        endpoint_url = f"{base_url}/{endpoint}"

    query_parts: list[str] = [f"$format={fmt}"]

    # Endpoint parameters as @Param='value' (quoted for strings).
    if params:
        for name, value in params.items():
            if isinstance(value, str):
                query_parts.append(f"@{name}='{value}'")
            else:
                query_parts.append(f"@{name}={value}")

    if filter:
        # Collapse whitespace after commas and opening parens, matching pixr.
        filter = re.sub(r",\s+", ",", filter)
        filter = re.sub(r"\(\s+", "(", filter)
        query_parts.append(f"$filter={filter}")

    if select:
        query_parts.append(f"$select={','.join(select)}")

    if orderby:
        query_parts.append(f"$orderby={orderby}")

    if top is not None:
        query_parts.append(f"$top={int(top)}")

    if skip is not None:
        warnings.warn(
            "Parameter 'skip' is not supported by the BCB PIX API; "
            "pagination with skip is not available. Use 'top' to limit results.",
            stacklevel=2,
        )

    query_string = "&".join(query_parts)
    # The API is picky about encoding: encode only spaces, like pixr.
    query_string = query_string.replace(" ", "%20")
    return f"{endpoint_url}?{query_string}"


def parse_year_month(year_month: Union[str, int, date, None]) -> Optional[str]:
    """Normalize a year-month to ``YYYYMM`` string form."""
    if year_month is None:
        return None
    if isinstance(year_month, (date, datetime)):
        return year_month.strftime("%Y%m")
    s = str(year_month)
    if not re.fullmatch(r"\d{6}", s):
        raise ValueError(
            f"Invalid year_month format: {s!r}. "
            "Expected YYYYMM (e.g. '202312' for December 2023)."
        )
    return s


def parse_date_param(value: Union[str, date, None]) -> Optional[str]:
    """Normalize a date to ``YYYY-MM-DD`` string form (for the ChavesPix endpoint)."""
    if value is None:
        return None
    if isinstance(value, (date, datetime)):
        return value.strftime("%Y-%m-%d")
    s = str(value)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        raise ValueError(
            f"Invalid date format: {s!r}. Expected YYYY-MM-DD (e.g. '2025-12-01')."
        )
    return s


def validate_columns(
    columns: Optional[Sequence[str]], valid_columns: Sequence[str]
) -> Optional[list[str]]:
    """Drop unknown column names (with a warning), preserving order."""
    if columns is None:
        return None
    valid_set = set(valid_columns)
    invalid = [c for c in columns if c not in valid_set]
    if invalid:
        warnings.warn(
            f"Unknown column(s) ignored: {invalid}. Valid columns: {list(valid_columns)}",
            stacklevel=2,
        )
    kept = [c for c in columns if c in valid_set]
    return kept or None


def format_orderby(
    orderby: Optional[str], valid_columns: Optional[Sequence[str]] = None
) -> Optional[str]:
    """Format an orderby spec into the OData ``"Column asc|desc"`` form.

    Accepts a leading ``-`` for descending order, or an already-formatted
    ``"Column desc"`` string (passed through after validation).
    """
    if not orderby:
        return None

    if orderby.startswith("-"):
        col, direction = orderby[1:], "desc"
    elif " " in orderby:
        # Already "Column asc/desc" form.
        col = orderby.split(" ", 1)[0]
        if valid_columns is not None and col not in valid_columns:
            warnings.warn(
                f"Invalid orderby column {col!r}; orderby will be ignored.",
                stacklevel=2,
            )
            return None
        return orderby
    else:
        col, direction = orderby, "asc"

    if valid_columns is not None and col not in valid_columns:
        warnings.warn(
            f"Invalid orderby column {col!r}; orderby will be ignored.",
            stacklevel=2,
        )
        return None

    return f"{col} {direction}"
