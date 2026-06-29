# pixbr — project notes for Claude

Python client for the **Brazilian Central Bank (BCB) PIX Open Data API**
(Olinda / OData). Python counterpart of the R package `pixr` (lives at
`../pixr`). Returns pandas DataFrames; hides the BCB's non-standard OData URL
syntax.

- **Package name:** `pixbr` (the obvious `pixpy` was already taken on PyPI).
- **Folder:** `/Users/leite/Github/pixbr` (was initially scaffolded as `pixpy`,
  then renamed).
- **Repo:** https://github.com/StrategicProjects/pixbr (public, branch `main`).
- **PyPI:** https://pypi.org/project/pixbr/ (v0.1.0 published).
- **Docs site:** https://strategicprojects.github.io/pixbr/ (MkDocs Material).
- **gh CLI** is authed as `milkway`, who is a member of the `StrategicProjects`
  org.

## Layout

```
src/pixbr/
  _odata.py      # pure URL builder + parsers (the tricky part; faithful to pixr)
  client.py      # PixClient (httpx + pandas) + typed endpoint accessors
  api.py         # module-level convenience functions (pixr-style names)
  aggregate.py   # pandas summaries (by institution, key type, state, region)
  utils.py       # format_brl, year_month_to_date, pix_endpoints, pix_columns
tests/           # pytest; respx for HTTP mocks
docs/            # MkDocs Material source
mkdocs.yml
.github/workflows/  ci.yml, publish.yml, docs.yml
```

## Design decisions

- API style: `PixClient` class (session/timeout/retries) **plus** standalone
  `get_pix_*` functions mirroring `pixr`. Stack: `httpx` + `pandas`.
- **OData URL building is the delicate part** (`_odata.build_url`): the BCB API
  is picky about encoding — only spaces are percent-encoded (`%20`), nothing
  else, exactly like `pixr::pix_request`. Filters collapse whitespace after
  commas/open-parens. Don't "fix" this with standard urlencode.
- Per-endpoint date param names differ on purpose: `ChavesPix` → `Data`
  (YYYY-MM-DD); `TransacoesPixPorMunicipio` → `DataBase`; `EstatisticasTransacoesPix`
  & `EstatisticasFraudesPix` → `Database` (all YYYYMM).
- `skip` is **not supported** by the BCB API → warn and ignore (don't add to URL).
- OData responses wrap rows in a top-level `value` field.

## Dev workflow

```bash
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"   # also ".[docs]"
.venv/bin/python -m pytest -q       # 20 tests
.venv/bin/mkdocs build --strict     # build docs locally
```

## CI/CD

- `ci.yml` — pytest matrix Python 3.9–3.13 on push/PR.
- `publish.yml` — on tag `v*` or GitHub Release, builds + publishes to PyPI via
  **Trusted Publishing (OIDC)**, no token. PyPI trusted publisher is configured
  (workflow `publish.yml`, environment `pypi`). To release: bump `version` in
  `pyproject.toml`, then `git tag vX.Y.Z && git push --tags`.
- `docs.yml` — builds MkDocs and deploys to GitHub Pages (source = GitHub
  Actions, already enabled).
- Actions pinned to Node-24 majors (checkout@v6, setup-python@v6,
  upload-artifact@v7, download-artifact@v8, upload-pages-artifact@v5,
  deploy-pages@v5). The old Node-20 warning from `upload-pages-artifact@v3`
  is gone since v5 (Apr 2026) switched to `upload-artifact@v7` / node24.

## Conventions

- Commit message trailer: `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.
- Docstrings are NumPy-style (mkdocstrings is configured for that). The docs
  Reference page is auto-generated from them — keep docstrings accurate.
- Match the green `#008060` identity from the `pixr` site in any docs styling.

## Possible next steps (not started)

- More tests (aggregations, client behaviour) — currently URL/parsers/utils.
- Optional: typed `from __future__` already used; consider adding `py.typed`
  marker if users want type info.
