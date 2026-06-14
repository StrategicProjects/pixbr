# Understanding PIX Data

## What is PIX?

PIX is Brazil's instant payment system, created and managed by the Brazilian
Central Bank (Banco Central do Brasil — BCB). Launched on November 16, 2020, it
enables instantaneous payments and transfers in Brazilian Real (BRL) 24/7,
including weekends and holidays.

Key features:

- **Instant** — transactions complete in seconds.
- **Free for individuals** — no fees for personal transfers.
- **Available 24/7** — any time, any day.
- **Multiple key types** — simple identifiers instead of full bank details.

## The PIX ecosystem

1. **SPI (Sistema de Pagamentos Instantâneos)** — the instant payment
   settlement system operated by the BCB.
2. **DICT (Diretório de Identificadores de Contas Transacionais)** — the
   directory that stores PIX key registrations and links them to accounts.
3. **PSP (Prestador de Serviços de Pagamento)** — payment service providers
   (financial institutions) that offer PIX.

### PIX key types

| Key type | Portuguese | Description |
|---|---|---|
| CPF | CPF | Individual taxpayer ID |
| CNPJ | CNPJ | Company taxpayer ID |
| Phone | Celular | Mobile phone with country code |
| Email | e-mail | Email address |
| Random | Aleatória (EVP) | System-generated UUID |

## Datasets available through pixbr

The BCB exposes four datasets. Use `pix_columns(...)` to see the columns of
each.

### 1. PIX keys stock — `ChavesPix`

Monthly snapshot of registered PIX keys, broken down by participant, user type
(PF/PJ), and key type. **Parameter:** `Data` in `YYYY-MM-DD` form.

```python
from pixbr import PixClient, pix_columns

pix_columns("keys")

client = PixClient()
keys = client.keys("2025-12-01")
cpf_keys = client.keys("2025-12-01", filter="TipoChave eq 'CPF'")
```

!!! tip "Month-end semantics"
    The API returns data for the **last day of the month** containing the given
    date — `keys("2025-12-01")` returns the 2025-12-31 snapshot.

### 2. Transactions by municipality — `TransacoesPixPorMunicipio`

Transaction values and counts per municipality, split by payer/receiver and
person type. **Parameter:** `DataBase` in `YYYYMM` form.

```python
muni = client.transactions_by_municipality("202512")
ne = client.transactions_by_municipality("202512", filter="Sigla_Regiao eq 'NE'")
```

Aggregate to higher levels with the convenience helpers:

```python
from pixbr import get_pix_transactions_by_state, get_pix_transactions_by_region

by_state = get_pix_transactions_by_state("202512")
by_region = get_pix_transactions_by_region("202512")
```

### 3. Transaction statistics — `EstatisticasTransacoesPix`

Granular breakdowns by payer/receiver type, region, age group, initiation
method, and transaction nature. **Parameter:** `Database` in `YYYYMM` form.

**Transaction nature:** `P2P`, `P2B`, `B2P`, `B2B`, `P2G`, `G2P`.
**Initiation methods:** `DICT`, `QRDN` (dynamic QR), `QRES` (static QR),
`MANU` (manual), `INIC` (payment initiator).

```python
stats = client.transaction_stats("202509")
p2p = client.transaction_stats("202509", filter="NATUREZA eq 'P2P'")
```

### 4. Fraud statistics (MED) — `EstatisticasFraudesPix`

Statistics from the Special Return Mechanism (Mecanismo Especial de Devolução),
covering fraud reports and refund requests. **Parameter:** `Database` in
`YYYYMM` form.

```python
fraud = client.fraud_stats("202509")
```
