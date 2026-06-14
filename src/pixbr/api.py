"""Module-level convenience functions mirroring the pixr function names.

Each call creates a short-lived :class:`~pixbr.client.PixClient`. For repeated
requests, instantiate a ``PixClient`` once and reuse it (it keeps an HTTP
connection pool open).
"""

from __future__ import annotations

from typing import List, Optional, Sequence

import pandas as pd

from . import aggregate
from .client import PixClient


def get_pix_keys(date: str, *, verbose: bool = True, **kwargs) -> pd.DataFrame:
    with PixClient(verbose=verbose) as c:
        return c.keys(date=date, verbose=verbose, **kwargs)


def get_pix_keys_summary(date: str, n_top: int = 20, *, verbose: bool = True) -> pd.DataFrame:
    with PixClient(verbose=verbose) as c:
        return aggregate.keys_summary(c, date=date, n_top=n_top)


def get_pix_keys_by_type(date: str, *, verbose: bool = True) -> pd.DataFrame:
    with PixClient(verbose=verbose) as c:
        return aggregate.keys_by_type(c, date=date)


def get_pix_transaction_stats(database: str, *, verbose: bool = True, **kwargs) -> pd.DataFrame:
    with PixClient(verbose=verbose) as c:
        return c.transaction_stats(database=database, verbose=verbose, **kwargs)


def get_pix_summary(database: str, group_by="NATUREZA", *, verbose: bool = True) -> pd.DataFrame:
    with PixClient(verbose=verbose) as c:
        return aggregate.transaction_summary(c, database=database, group_by=group_by)


def get_pix_transactions_by_municipality(
    database: str, *, verbose: bool = True, **kwargs
) -> pd.DataFrame:
    with PixClient(verbose=verbose) as c:
        return c.transactions_by_municipality(database=database, verbose=verbose, **kwargs)


def get_pix_transactions_by_state(database: str, *, verbose: bool = True) -> pd.DataFrame:
    with PixClient(verbose=verbose) as c:
        return aggregate.transactions_by_state(c, database=database)


def get_pix_transactions_by_region(database: str, *, verbose: bool = True) -> pd.DataFrame:
    with PixClient(verbose=verbose) as c:
        return aggregate.transactions_by_region(c, database=database)


def get_pix_fraud_stats(database: str, *, verbose: bool = True, **kwargs) -> pd.DataFrame:
    with PixClient(verbose=verbose) as c:
        return c.fraud_stats(database=database, verbose=verbose, **kwargs)


def _get_multi(method_name: str, databases: Sequence[str], **kwargs) -> pd.DataFrame:
    frames: List[pd.DataFrame] = []
    with PixClient(verbose=False) as c:
        method = getattr(c, method_name)
        for db in databases:
            try:
                frames.append(method(database=db, verbose=False, **kwargs))
            except Exception:  # noqa: BLE001 - keep going on per-month failures
                frames.append(pd.DataFrame())
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def get_pix_transaction_stats_multi(databases: Sequence[str], **kwargs) -> pd.DataFrame:
    return _get_multi("transaction_stats", databases, **kwargs)


def get_pix_fraud_stats_multi(databases: Sequence[str], **kwargs) -> pd.DataFrame:
    return _get_multi("fraud_stats", databases, **kwargs)


def pix_ping() -> pd.DataFrame:
    with PixClient() as c:
        return c.ping()


def pix_query(endpoint: str, params: Optional[dict] = None, *, verbose: bool = True, **kwargs) -> pd.DataFrame:
    with PixClient(verbose=verbose) as c:
        return c.query(endpoint, params, verbose=verbose, **kwargs)


def pix_url(endpoint: str, params: Optional[dict] = None, **kwargs) -> str:
    with PixClient(verbose=False) as c:
        return c.build_url(endpoint, params, **kwargs)
