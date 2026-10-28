# pixbr — project notes for Claude

Python client for the **Brazilian Central Bank (BCB) PIX Open Data API**
(Olinda / OData). Python counterpart of the R package `pixr` (lives at
`../pixr`). Returns pandas DataFrames; hides the BCB's non-standard OData URL
syntax.

- **Package name:** `pixbr` (the obvious `pixpy` was already taken on PyPI).
- **Folder:** `/Users/leite/Github/pixbr` (was initially scaffolded as `pixpy`,
  then renamed).
- **Repo:** https://github.com/StrategicProjects/pixbr (public, branch `main`).
- **PyPI:** https://pypi.org/project/pixbr/ (v0.2.0 published 2026-10-28,
  via Trusted Publishing on tag push).
- **Docs site:** https://strategicprojects.github.io/pixbr/ (MkDocs Material).
- **gh CLI** is authed as `milkway`, who is a member of the `StrategicProjects`
  org.

## Endpoints

Six BCB endpoints (since 0.2.0): the original four plus `CnaePorteRecebedor`
(`cnae_stats`, receiver CNAE/size/MEI) and `PixUsuariosCadastradosDICT`
(`dict_users`, monthly DICT users series, **no parameter**, `DataGraficosPix`
parsed to datetime). **Gotcha:** on `CnaePorteRecebedor` (and the municipality
endpoint) the `Database` param selects the data *snapshot*, not the month —
the response mixes several `AnoMes`; filter with `AnoMes eq YYYYMM` for one
month. All data is monthly. To check for new endpoints, diff the OData
`$metadata` (EntityType/FunctionImport) against `ENDPOINTS` in `client.py`.

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
  assets/        # logo.svg (hex sticker), logo.png, favicon.svg, logo-wordmark.svg
mkdocs.yml
.github/workflows/  ci.yml, publish.yml, docs.yml
```

## Branding / logo

- Hex-sticker logo adapted from the R package `pixr` (`../pixr/man/figures/logo.svg`):
  same official PIX mark/wordmark on a hexagon, recoloured to pixbr's green
  identity (`#008060`, gradient `#13a884`→`#008060`) with a hand-built **monoline
  "br"** matching the PIX wordmark (stroke ~3.6, round caps). All vector, no font
  dependency. Wordmark metrics: baseline y=147.25, x-height top y=111, ascender/
  diamond top ~95; PIX diamond-mark bbox centre (109.25, 101.0).
- Assets in `docs/assets/`: `logo.svg`/`logo.png` (full hex sticker),
  `favicon.svg` (hex + enlarged white mark, centred on hex centroid 128,128),
  `logo-wordmark.svg` (white transparent wordmark for the green header bar).
- Wired in `mkdocs.yml` (`theme.logo` = logo-wordmark.svg, `theme.favicon`).
  Shown right-aligned in both `README.md` (absolute raw URL so it renders on
  PyPI too) and `docs/index.md` (relative `assets/logo.svg`).
- Render/measure with `rsvg-convert` (installed); inkscape is not.

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
.venv/bin/python -m pytest -q       # 30 tests
.venv/bin/mkdocs build --strict     # build docs locally
```

## CI/CD

- `ci.yml` — pytest matrix Python 3.10–3.14 on push/PR (3.9 dropped: EOL
  Oct 2025 and absent from Ubuntu 26.04 runners; `requires-python >=3.10`
  takes effect on PyPI at the next release).
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

- Author list and order are canonical in `../alepe/DESCRIPTION` (Leite,
  Wasiliew, Vasconcelos, Amorim, Bezerra, Nascimento Barreto, all with
  ORCIDs); keep `pyproject.toml`, `CITATION.cff` and `.zenodo.json` aligned.

- Commit message trailer: use the Claude Code attribution line for the model
  in use (e.g. `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`).
- Docstrings are NumPy-style (mkdocstrings is configured for that). The docs
  Reference page is auto-generated from them — keep docstrings accurate.
- Match the green `#008060` identity from the `pixr` site in any docs styling.

## Possible next steps (not started)

- More tests (aggregations, client behaviour) — currently URL/parsers/utils
  plus respx-mocked client tests for the new endpoints.
- Optional: typed `from __future__` already used; consider adding `py.typed`
  marker if users want type info.
