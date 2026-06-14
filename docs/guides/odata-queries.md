# Working with OData Queries

The BCB PIX Open Data API uses the [OData](https://www.odata.org/) protocol.
`pixbr` exposes the common OData parameters on every endpoint method:
`filter`, `columns` (`$select`), `orderby`, and `top`.

## Endpoint parameters

Each endpoint takes a specific date/database parameter:

| Endpoint | Parameter | Format | `pixbr` call |
|---|---|---|---|
| `ChavesPix` | `Data` | YYYY-MM-DD | `client.keys("2025-12-01")` |
| `TransacoesPixPorMunicipio` | `DataBase` | YYYYMM | `client.transactions_by_municipality("202512")` |
| `EstatisticasTransacoesPix` | `Database` | YYYYMM | `client.transaction_stats("202509")` |
| `EstatisticasFraudesPix` | `Database` | YYYYMM | `client.fraud_stats("202509")` |

## Filtering with `filter`

```python
from pixbr import PixClient
client = PixClient()

client.transactions_by_municipality("202512", filter="Estado eq 'MARANHÃO'")
client.transactions_by_municipality("202512", filter="Sigla_Regiao eq 'NE'")
client.transaction_stats("202509", filter="NATUREZA eq 'P2P'")
client.keys("2025-12-01", filter="TipoChave eq 'CPF'")
```

### Comparison operators

| Operator | Meaning | Example |
|---|---|---|
| `eq` | equal | `"Estado eq 'SÃO PAULO'"` |
| `ne` | not equal | `"NATUREZA ne 'P2P'"` |
| `gt` | greater than | `"VALOR gt 1000"` |
| `ge` | greater or equal | `"QUANTIDADE ge 100"` |
| `lt` | less than | `"VALOR lt 5000"` |
| `le` | less or equal | `"qtdChaves le 1000"` |

```python
client.transaction_stats("202509", filter="VALOR gt 10000")
client.keys("2025-12-01", filter="qtdChaves le 1000")
```

### Logical operators

Combine conditions with `and` / `or`:

```python
client.transaction_stats(
    "202509",
    filter="NATUREZA eq 'P2P' and PAG_REGIAO eq 'SUDESTE'",
)

client.transactions_by_municipality(
    "202512",
    filter="Estado eq 'SÃO PAULO' or Estado eq 'RIO DE JANEIRO'",
)
```

!!! note "String values use single quotes"
    OData string literals are single-quoted inside the filter, exactly as in
    the examples above. Accented names (e.g. `MARANHÃO`) work as-is — `pixbr`
    encodes the URL correctly.

## Selecting columns

Pass `columns` to return only the fields you need. Unknown columns are dropped
with a warning.

```python
client.transaction_stats(
    "202509",
    columns=["NATUREZA", "PAG_REGIAO", "VALOR", "QUANTIDADE"],
)
```

## Ordering with `orderby`

```python
client.transaction_stats("202509", orderby="VALOR desc")
client.keys("2025-12-01", orderby="qtdChaves desc", top=10)
```

## Limiting with `top`

```python
client.transactions_by_municipality("202512", orderby="VL_PagadorPF desc", top=100)
```

!!! warning "`skip` is not supported"
    The BCB PIX API does not implement `$skip`. Passing `skip` emits a warning
    and is ignored; use `top` to bound the result size.

## Inspecting the URL

`build_url` (or the module-level `pix_url`) returns the request URL **without
sending it** — handy for debugging the OData syntax:

```python
client.build_url(
    "EstatisticasTransacoesPix", {"Database": "202509"},
    filter="NATUREZA eq 'P2P'", top=10,
)
# .../EstatisticasTransacoesPix(Database=@Database)
#   ?$format=json&@Database='202509'&$filter=NATUREZA%20eq%20'P2P'&$top=10
```

## Raw queries

For endpoints or parameters not covered by the typed methods, use `query`
(or `pix_query`):

```python
client.query(
    "EstatisticasTransacoesPix",
    {"Database": "202509"},
    filter="NATUREZA eq 'P2B'",
    top=50,
)
```
