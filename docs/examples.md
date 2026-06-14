# Examples

## Top regions by P2P value

Which Brazilian regions paid the most via person-to-person PIX in September
2025, and what was the average ticket?

```python
from pixbr import PixClient, format_brl

client = PixClient()

stats = client.transaction_stats(
    "202509",
    filter="NATUREZA eq 'P2P'",
    columns=["PAG_REGIAO", "VALOR", "QUANTIDADE"],
)

by_region = (
    stats.groupby("PAG_REGIAO", as_index=False)
    .agg(total_value=("VALOR", "sum"), total_count=("QUANTIDADE", "sum"))
    .assign(avg_ticket=lambda d: d["total_value"] / d["total_count"])
    .sort_values("total_value", ascending=False)
)

by_region["total_value"] = by_region["total_value"].map(format_brl)
by_region["avg_ticket"] = by_region["avg_ticket"].map(format_brl)
print(by_region.to_string(index=False))
```

The same aggregation is a one-liner with the convenience helper:

```python
from pixbr import get_pix_summary

get_pix_summary("202509", group_by="PAG_REGIAO")
# columns: PAG_REGIAO, total_value, total_count, avg_value, n_records
```

## Key-type mix by institution

```python
from pixbr import PixClient
from pixbr import aggregate

client = PixClient()

# Top institutions by total registered keys.
aggregate.keys_summary(client, "2025-12-01", n_top=10)

# Totals by key type and user nature.
aggregate.keys_by_type(client, "2025-12-01")
```

## A quarterly time series

```python
from pixbr import get_pix_transaction_stats_multi

q3 = get_pix_transaction_stats_multi(["202507", "202508", "202509"])
monthly = q3.groupby("AnoMes")["VALOR"].sum()
print(monthly)
```

## Top municipalities by value received

```python
from pixbr import PixClient

client = PixClient()

muni = client.transactions_by_municipality(
    "202512",
    columns=["Municipio", "Estado", "VL_RecebedorPF", "VL_RecebedorPJ"],
    orderby="VL_RecebedorPF desc",
    top=20,
)
muni["total_recebido"] = muni["VL_RecebedorPF"] + muni["VL_RecebedorPJ"]
muni.sort_values("total_recebido", ascending=False).head(10)
```

## Checking connectivity

```python
from pixbr import pix_ping

pix_ping()   # status for all four endpoints
```
