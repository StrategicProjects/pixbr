# pixbr

[![CI](https://github.com/StrategicProjects/pixbr/actions/workflows/ci.yml/badge.svg)](https://github.com/StrategicProjects/pixbr/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/pixbr.svg)](https://pypi.org/project/pixbr/)
[![Python versions](https://img.shields.io/pypi/pyversions/pixbr.svg)](https://pypi.org/project/pixbr/)
[![License: MIT](https://img.shields.io/pypi/l/pixbr.svg)](https://github.com/StrategicProjects/pixbr/blob/main/LICENSE)

**pixbr** is a Python client for the [Brazilian Central Bank (BCB) PIX Open Data
API](https://dadosabertos.bcb.gov.br/dataset/pix). It hides the BCB's unusual
OData URL syntax and returns [pandas](https://pandas.pydata.org/) DataFrames,
so you can go straight from a query to analysis.

It is the Python counterpart of the R package
[`pixr`](https://github.com/StrategicProjects/pixr).

## Features

- **Four endpoints, one interface** — PIX keys, transactions by municipality,
  transaction statistics, and fraud (MED) statistics.
- **pandas-native** — every call returns a DataFrame with numeric columns
  already coerced.
- **Full OData support** — `filter`, `select` (`columns`), `orderby`, `top`.
- **Two styles** — a reusable `PixClient` or `pixr`-style convenience functions.
- **Aggregation helpers** — summaries by institution, key type, state, region.

## Install

```bash
pip install pixbr
```

## Quick taste

```python
from pixbr import PixClient

client = PixClient()
stats = client.transaction_stats("202509", filter="NATUREZA eq 'P2P'")
stats.head()
```

Head to **[Get Started](getting-started.md)** for the full tour, or the
**[Reference](reference.md)** for every function.

## Useful links

- [BCB PIX Open Data Portal](https://dadosabertos.bcb.gov.br/dataset/pix)
- [API Swagger documentation](https://olinda.bcb.gov.br/olinda/servico/Pix_DadosAbertos/versao/v1/swagger-ui3#/)
- [BCB PIX official page](https://www.bcb.gov.br/estabilidadefinanceira/pix)
