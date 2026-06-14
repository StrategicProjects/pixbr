# API Reference

## Client

::: pixbr.PixClient

## Convenience functions

These mirror the R package `pixr`. Each creates a short-lived
[`PixClient`][pixbr.PixClient].

### PIX keys

::: pixbr.get_pix_keys
::: pixbr.get_pix_keys_summary
::: pixbr.get_pix_keys_by_type

### Transactions by municipality

::: pixbr.get_pix_transactions_by_municipality
::: pixbr.get_pix_transactions_by_state
::: pixbr.get_pix_transactions_by_region

### Transaction statistics

::: pixbr.get_pix_transaction_stats
::: pixbr.get_pix_summary
::: pixbr.get_pix_transaction_stats_multi

### Fraud statistics

::: pixbr.get_pix_fraud_stats
::: pixbr.get_pix_fraud_stats_multi

## API utilities

::: pixbr.pix_ping
::: pixbr.pix_query
::: pixbr.pix_url
::: pixbr.pix_endpoints
::: pixbr.pix_columns

## Data helpers

::: pixbr.year_month_to_date
::: pixbr.format_brl

## Errors

::: pixbr.PixApiError
