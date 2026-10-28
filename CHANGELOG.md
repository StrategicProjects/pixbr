# Changelog

## Unreleased

- Dropped support for Python 3.9 (end of life since October 2025);
  requires-python is now >=3.10. CI matrix updated to 3.10-3.14.

## 0.2.0

New endpoints added upstream by the BCB, mirroring pixr 0.1.1:

- `PixClient.cnae_stats()` / `get_pix_cnae_stats()` — `CnaePorteRecebedor`
  endpoint: PIX statistics by receiver CNAE section, company size, and MEI
  status. Note: `database` selects the data snapshot; filter on `AnoMes`
  for a single month.
- `PixClient.dict_users()` / `get_pix_dict_users()` —
  `PixUsuariosCadastradosDICT` endpoint: monthly series of users registered
  in the DICT (no parameter; `DataGraficosPix` parsed to datetime).
- `pix_columns("fraud")` now documents the full 24-column fraud schema;
  `fraud_stats()` validates `columns` against it and coerces every numeric
  column (the old pattern-based coercion missed `Qtde*` and `Percentual*`
  columns, which stayed as strings).
- `pix_endpoints()` and `pix_ping()` now cover all six endpoints.
- Author order aligned with the R packages (pixr, alepe).

## 0.1.1

Metadata release (no code changes).

- Corrected author name spellings (André Leite, Marcos Wasiliew) in package
  metadata, LICENSE, and docs; added Carlos Amorim to the author list.
- Added `CITATION.cff` and `.zenodo.json` for citation metadata and Zenodo
  archiving (DOI).

## 0.1.0

First release.

- `PixClient` — HTTP client (httpx + pandas) for the BCB PIX Open Data API,
  with typed accessors for the four endpoints: `.keys()`,
  `.transactions_by_municipality()`, `.transaction_stats()`, `.fraud_stats()`.
- Module-level convenience functions mirroring the R package `pixr`
  (`get_pix_keys`, `get_pix_transaction_stats`, `get_pix_summary`, ...).
- Aggregation helpers: summaries by institution, key type, state, and region.
- OData URL building faithful to `pixr` (spaces-only encoding, per-endpoint
  date parameter names, `skip`-not-supported warning).
- Utilities: `format_brl`, `year_month_to_date`, `pix_endpoints`,
  `pix_columns`, `pix_ping`, `pix_query`, `pix_url`.
