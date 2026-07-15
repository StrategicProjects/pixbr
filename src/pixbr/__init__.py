"""pixbr — access the Brazilian Central Bank PIX Open Data API from Python.

Two ways to use it:

1. A reusable client (recommended for multiple requests)::

       from pixbr import PixClient
       client = PixClient()
       df = client.transaction_stats("202509", filter="NATUREZA eq 'P2P'")

2. Module-level convenience functions mirroring the R package ``pixr``::

       from pixbr import get_pix_transaction_stats
       df = get_pix_transaction_stats("202509")
"""

from __future__ import annotations

from .client import ENDPOINTS, PixApiError, PixClient
from .utils import (
    format_brl,
    pix_columns,
    pix_endpoints,
    year_month_to_date,
)
from .api import (
    get_pix_fraud_stats,
    get_pix_fraud_stats_multi,
    get_pix_keys,
    get_pix_keys_by_type,
    get_pix_keys_summary,
    get_pix_summary,
    get_pix_transaction_stats,
    get_pix_transaction_stats_multi,
    get_pix_transactions_by_municipality,
    get_pix_transactions_by_region,
    get_pix_transactions_by_state,
    pix_ping,
    pix_query,
    pix_url,
)

__version__ = "0.1.1"

__all__ = [
    "PixClient",
    "PixApiError",
    "ENDPOINTS",
    # utils
    "format_brl",
    "pix_columns",
    "pix_endpoints",
    "year_month_to_date",
    # convenience functions
    "get_pix_keys",
    "get_pix_keys_summary",
    "get_pix_keys_by_type",
    "get_pix_transaction_stats",
    "get_pix_transaction_stats_multi",
    "get_pix_summary",
    "get_pix_transactions_by_municipality",
    "get_pix_transactions_by_state",
    "get_pix_transactions_by_region",
    "get_pix_fraud_stats",
    "get_pix_fraud_stats_multi",
    "pix_ping",
    "pix_query",
    "pix_url",
]
