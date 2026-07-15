# Changelog

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
