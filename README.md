# pixbr

[![CI](https://github.com/StrategicProjects/pixbr/actions/workflows/ci.yml/badge.svg)](https://github.com/StrategicProjects/pixbr/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/pixbr.svg)](https://pypi.org/project/pixbr/)
[![Python versions](https://img.shields.io/pypi/pyversions/pixbr.svg)](https://pypi.org/project/pixbr/)
[![License: MIT](https://img.shields.io/pypi/l/pixbr.svg)](https://github.com/StrategicProjects/pixbr/blob/main/LICENSE)
[![Docs](https://img.shields.io/badge/docs-online-008060.svg)](https://strategicprojects.github.io/pixbr/)

Python client for the **Brazilian Central Bank (BCB) PIX Open Data API**
([Olinda / OData service](https://olinda.bcb.gov.br/olinda/servico/Pix_DadosAbertos/versao/v1/aplicacao)).
It hides the BCB's unusual OData URL syntax and returns
[pandas](https://pandas.pydata.org/) DataFrames.

📖 **Documentation:** <https://strategicprojects.github.io/pixbr/>

This is the Python counterpart of the R package
[`pixr`](https://github.com/StrategicProjects/pixr).

## Installation

```bash
pip install pixbr        # once published
# or, from source:
pip install -e ".[dev]"
```

## Quick start

Reusable client (recommended for multiple requests):

```python
from pixbr import PixClient

client = PixClient()

# PIX keys stock by participant (date in YYYY-MM-DD)
keys = client.keys("2025-12-01", filter="TipoChave eq 'CPF'", top=100)

# Transaction statistics (database in YYYYMM)
stats = client.transaction_stats("202509", filter="NATUREZA eq 'P2P'")

# Transactions by municipality
muni = client.transactions_by_municipality("202512", filter="Sigla_Regiao eq 'NE'")

# Fraud statistics (MED)
fraud = client.fraud_stats("202509", top=100)
```

Module-level convenience functions mirror the `pixr` names:

```python
from pixbr import get_pix_transaction_stats, get_pix_summary, format_brl

df = get_pix_transaction_stats("202509")
summary = get_pix_summary("202509", group_by="PAG_REGIAO")
format_brl(1234567.89)   # 'R$ 1.234.567,89'
```

## Worked example

A small end-to-end analysis: which Brazilian regions paid the most via PIX in
September 2025, and what was the average ticket per person-to-person transfer?

```python
from pixbr import PixClient, format_brl

client = PixClient()

# 1. Pull person-to-person transaction statistics for the month.
stats = client.transaction_stats(
    "202509",
    filter="NATUREZA eq 'P2P'",
    columns=["PAG_REGIAO", "VALOR", "QUANTIDADE"],
)

# 2. Aggregate by payer region (the data comes pre-broken-down, so we sum it).
by_region = (
    stats.groupby("PAG_REGIAO", as_index=False)
    .agg(total_value=("VALOR", "sum"), total_count=("QUANTIDADE", "sum"))
    .assign(avg_ticket=lambda d: d["total_value"] / d["total_count"])
    .sort_values("total_value", ascending=False)
)

# 3. Present it with Brazilian currency formatting.
by_region["total_value"] = by_region["total_value"].map(format_brl)
by_region["avg_ticket"] = by_region["avg_ticket"].map(format_brl)
print(by_region.to_string(index=False))
```

The same aggregation is available as a one-liner via the convenience helper:

```python
from pixbr import get_pix_summary

summary = get_pix_summary("202509", group_by="PAG_REGIAO")
# columns: PAG_REGIAO, total_value, total_count, avg_value, n_records
```

Fetching several months at once and combining into a single DataFrame:

```python
from pixbr import get_pix_transaction_stats_multi

q3 = get_pix_transaction_stats_multi(["202507", "202508", "202509"])
monthly = q3.groupby("AnoMes")["VALOR"].sum()
```

Debugging a request without sending it (useful to inspect the OData URL):

```python
client.build_url("EstatisticasTransacoesPix", {"Database": "202509"},
                 filter="NATUREZA eq 'P2P'", top=10)
# https://olinda.bcb.gov.br/.../EstatisticasTransacoesPix(Database=@Database)
#   ?$format=json&@Database='202509'&$filter=NATUREZA%20eq%20'P2P'&$top=10
```

## Endpoints

| Endpoint | Parameter | `PixClient` method | Convenience function |
|---|---|---|---|
| `ChavesPix` | `Data` (YYYY-MM-DD) | `.keys()` | `get_pix_keys()` |
| `TransacoesPixPorMunicipio` | `DataBase` (YYYYMM) | `.transactions_by_municipality()` | `get_pix_transactions_by_municipality()` |
| `EstatisticasTransacoesPix` | `Database` (YYYYMM) | `.transaction_stats()` | `get_pix_transaction_stats()` |
| `EstatisticasFraudesPix` | `Database` (YYYYMM) | `.fraud_stats()` | `get_pix_fraud_stats()` |

Use `pix_endpoints()` and `pix_columns("keys"|"municipality"|"stats"|"fraud")`
to inspect available endpoints and columns.

## OData query parameters

All endpoint methods accept the common OData parameters:

- `filter` — OData filter expression, e.g. `"NATUREZA eq 'P2P' and PAG_REGIAO eq 'SUDESTE'"`
- `columns` — list of columns to select (unknown columns are dropped with a warning)
- `orderby` — `"Column"` (asc) or `"Column desc"`
- `top` — maximum number of records

> **Note:** `skip` is **not supported** by the BCB PIX API; passing it emits a
> warning and is ignored. Use `top` to limit results.

## Notes

- `PixClient(timeout=..., max_retries=..., verbose=...)` configures the HTTP
  session. The default timeout is 120s — the BCB API can be slow for large
  queries.
- `client.build_url(...)` / `pix_url(...)` return the request URL without
  sending it (handy for debugging).
- `client.ping()` / `pix_ping()` test connectivity to all four endpoints.

## License

MIT
