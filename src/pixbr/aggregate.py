"""Convenience aggregations over the raw endpoint data (pandas-based).

These mirror the dplyr-based summaries in ``pixr`` (get_pix_summary,
get_pix_keys_summary, get_pix_transactions_by_state, etc.).
"""

from __future__ import annotations

from typing import List, Sequence, Union

import pandas as pd

from .client import PixClient


def keys_summary(client: PixClient, date: str, n_top: int = 20) -> pd.DataFrame:
    """Total keys by institution, sorted descending, limited to ``n_top``."""
    data = client.keys(date=date)
    if data.empty:
        return data
    agg = (
        data.groupby(["Nome", "ISPB"])
        .agg(
            total_keys=("qtdChaves", "sum"),
            n_key_types=("TipoChave", "nunique"),
        )
        .reset_index()
    )
    pf = data[data["NaturezaUsuario"] == "PF"].groupby(["Nome", "ISPB"])["qtdChaves"].sum()
    pj = data[data["NaturezaUsuario"] == "PJ"].groupby(["Nome", "ISPB"])["qtdChaves"].sum()
    agg["pf_keys"] = agg.set_index(["Nome", "ISPB"]).index.map(pf).fillna(0).to_numpy()
    agg["pj_keys"] = agg.set_index(["Nome", "ISPB"]).index.map(pj).fillna(0).to_numpy()
    return agg.sort_values("total_keys", ascending=False).head(n_top).reset_index(drop=True)


def keys_by_type(client: PixClient, date: str) -> pd.DataFrame:
    """Total keys grouped by key type and user nature."""
    data = client.keys(date=date)
    if data.empty:
        return data
    return (
        data.groupby(["TipoChave", "NaturezaUsuario"])
        .agg(total_keys=("qtdChaves", "sum"), n_institutions=("ISPB", "nunique"))
        .reset_index()
        .sort_values("total_keys", ascending=False)
        .reset_index(drop=True)
    )


def transaction_summary(
    client: PixClient, database: str, group_by: Union[str, Sequence[str]] = "NATUREZA"
) -> pd.DataFrame:
    """Aggregate transaction statistics by one or more grouping columns."""
    data = client.transaction_stats(database=database)
    if data.empty:
        return data
    keys = [group_by] if isinstance(group_by, str) else list(group_by)
    grouped = data.groupby(keys)
    out = grouped.agg(
        total_value=("VALOR", "sum"),
        total_count=("QUANTIDADE", "sum"),
        n_records=("VALOR", "size"),
    ).reset_index()
    out["avg_value"] = out["total_value"] / out["total_count"]
    return out.sort_values("total_value", ascending=False).reset_index(drop=True)


_MUNI_SUM_COLS = [
    "VL_PagadorPF", "QT_PagadorPF", "VL_PagadorPJ", "QT_PagadorPJ",
    "VL_RecebedorPF", "QT_RecebedorPF", "VL_RecebedorPJ", "QT_RecebedorPJ",
]


def _muni_lower(col: str) -> str:
    return col.lower().replace("pagadorpf", "pagador_pf").replace("pagadorpj", "pagador_pj") \
        .replace("recebedorpf", "recebedor_pf").replace("recebedorpj", "recebedor_pj")


def transactions_by_state(client: PixClient, database: str) -> pd.DataFrame:
    """Aggregate municipality data to the state level."""
    return _aggregate_geo(
        client, database,
        keys=["AnoMes", "Estado_Ibge", "Estado", "Sigla_Regiao", "Regiao"],
        count_name="n_municipalities",
        count_kind="size",
    )


def transactions_by_region(client: PixClient, database: str) -> pd.DataFrame:
    """Aggregate municipality data to the region level."""
    data = client.transactions_by_municipality(database=database)
    if data.empty:
        return data
    agg = {c: "sum" for c in _MUNI_SUM_COLS if c in data.columns}
    out = data.groupby(["AnoMes", "Sigla_Regiao", "Regiao"]).agg(
        n_states=("Estado_Ibge", "nunique"),
        n_municipalities=("Estado_Ibge", "size"),
        **{_muni_lower(c): (c, "sum") for c in _MUNI_SUM_COLS if c in data.columns},
    ).reset_index()
    sort_col = "vl_pagador_pf" if "vl_pagador_pf" in out.columns else out.columns[-1]
    return out.sort_values(sort_col, ascending=False).reset_index(drop=True)


def _aggregate_geo(
    client: PixClient,
    database: str,
    keys: List[str],
    count_name: str,
    count_kind: str,
) -> pd.DataFrame:
    data = client.transactions_by_municipality(database=database)
    if data.empty:
        return data
    out = data.groupby(keys).agg(
        **{count_name: ("AnoMes", count_kind)},
        **{_muni_lower(c): (c, "sum") for c in _MUNI_SUM_COLS if c in data.columns},
    ).reset_index()
    sort_col = "vl_pagador_pf" if "vl_pagador_pf" in out.columns else out.columns[-1]
    return out.sort_values(sort_col, ascending=False).reset_index(drop=True)
