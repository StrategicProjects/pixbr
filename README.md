# pixbr

Python client for the **Brazilian Central Bank (BCB) PIX Open Data API**
([Olinda / OData service](https://olinda.bcb.gov.br/olinda/servico/Pix_DadosAbertos/versao/v1/aplicacao)).
It hides the BCB's unusual OData URL syntax and returns
[pandas](https://pandas.pydata.org/) DataFrames.

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
