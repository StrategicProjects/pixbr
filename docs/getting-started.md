# Get Started

## Installation

```bash
pip install pixbr
```

`pixbr` requires Python 3.9+ and depends only on
[`httpx`](https://www.python-httpx.org/) and
[`pandas`](https://pandas.pydata.org/).

## Two ways to use it

### 1. A reusable client (recommended)

`PixClient` keeps an HTTP connection pool open, so it is the right choice when
you make several requests.

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

`PixClient` is also a context manager:

```python
with PixClient(timeout=180) as client:
    df = client.transaction_stats("202509")
```

### 2. Convenience functions

These mirror the `pixr` names and create a short-lived client per call.

```python
from pixbr import get_pix_transaction_stats, get_pix_summary, format_brl

df = get_pix_transaction_stats("202509")
summary = get_pix_summary("202509", group_by="PAG_REGIAO")
format_brl(1234567.89)   # 'R$ 1.234.567,89'
```

## Endpoints at a glance

| Endpoint | Parameter | `PixClient` method | Convenience function |
|---|---|---|---|
| `ChavesPix` | `Data` (YYYY-MM-DD) | `.keys()` | `get_pix_keys()` |
| `TransacoesPixPorMunicipio` | `DataBase` (YYYYMM) | `.transactions_by_municipality()` | `get_pix_transactions_by_municipality()` |
| `EstatisticasTransacoesPix` | `Database` (YYYYMM) | `.transaction_stats()` | `get_pix_transaction_stats()` |
| `EstatisticasFraudesPix` | `Database` (YYYYMM) | `.fraud_stats()` | `get_pix_fraud_stats()` |

Inspect endpoints and columns programmatically:

```python
from pixbr import pix_endpoints, pix_columns

pix_endpoints()                # DataFrame describing all endpoints
pix_columns("stats")           # columns for the transaction-stats endpoint
```

## Configuration

```python
PixClient(
    timeout=120,      # seconds; the BCB API can be slow for large queries
    max_retries=3,    # retries on transport errors
    verbose=True,     # log progress at INFO level
)
```

!!! note "`skip` is not supported"
    The BCB PIX API does not support `$skip` pagination. Passing `skip` emits a
    warning and is ignored — use `top` to limit results.

## Next steps

- **[Understanding PIX Data](guides/understanding-pix-data.md)** — what each
  dataset contains.
- **[Working with OData Queries](guides/odata-queries.md)** — filtering,
  ordering, selecting.
- **[Examples](examples.md)** — end-to-end analyses.
