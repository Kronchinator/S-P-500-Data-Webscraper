# StockOracle sector dashboard

This project builds a local dashboard for comparing stocks inside the 11 SPDR sector ETFs, which is effectively a sector-sliced view of the S&P 500.

I made it because screening stocks one ticker at a time is slow, and sector context matters. A company can look cheap in isolation but still be a weak candidate beside the rest of its sector. This tool pulls ETF holdings, fetches StockOracle valuation data, scores each ticker, then writes a small HTML dashboard for review.

It is a research tool, not financial advice. The point is to narrow a large watchlist into names worth reading properly.

## What it covers

The dataset starts from the holdings of these SPDR sector ETFs:

- XLK, technology
- XLF, financials
- XLE, energy
- XLV, healthcare
- XLY, consumer discretionary
- XLP, consumer staples
- XLI, industrials
- XLB, materials
- XLRE, real estate
- XLC, communication services
- XLU, utilities

For each ticker, the scraper collects StockOracle summary data and calculates a few extra fields for ranking.

## What the dashboard shows

- Oracle value and DCF value
- DCF upside
- Quality score
- Opportunity score
- Signal bucket: core candidate, watchlist, speculative, neutral, or avoid / expensive
- Profitability
- Financial strength
- Oracle moat
- Valuation
- Sector filters and a ranked candidate shortlist

The scoring is deliberately simple. It does not try to predict price. It tries to answer a more useful first question: "Which names deserve more attention?"

## Data sources

### SSGA holdings

Each SPDR ETF page exposes a daily holdings workbook. The script downloads the workbook and extracts the current tickers.

### StockOracle

The scraper uses these discovered endpoints:

```text
GET  /api/stock-symbol/get-symbol-detail?symbol={ticker}
POST /api/stock-detail/pagi6/{stockId}
GET  /api/stock-detail-intrinsic/get-dcf-automation/{stockGuid}
GET  /api/stock-detail-intrinsic/get-pp-automation/{stockGuid}
```

A StockOracle bearer token is required. The token rotates often, roughly every 90 minutes, so it needs to be refreshed before running the scraper. You also need a StockOracle subscription for authenticated endpoint access.

Credentials are kept out of the repo.

## Setup

Create a local credentials file:

```bash
cp config/credentials.example.json config/credentials.json
```

Paste your current StockOracle bearer token into `config/credentials.json`, then install dependencies:

```bash
pip install -r requirements.txt
```

## Run

Build the dataset:

```bash
python src/build_dataset.py
```

Build the dashboard:

```bash
python src/build_dashboard.py
```

Open:

```text
dashboard/index.html
```

Run tests:

```bash
python -m pytest -q
```

## Project structure

```text
src/ssga_holdings.py          SPDR holdings download and parsing
src/stockoracle_client.py     StockOracle API client
src/dashboard_metrics.py      scoring and signal labels
src/build_dataset.py          dataset builder
src/build_dashboard.py        static dashboard builder
dashboard/index.html          generated dashboard
config/credentials.example.json
tests/test_dashboard_metrics.py
```

## Current limits

- The StockOracle token must be supplied manually and refreshed when it expires.
- The score is a triage score, not a buy or sell signal.
- API responses can change. The tests cover the scoring layer, not the availability of the external service.
- The generated dataset should be refreshed before using it for any current analysis.

## Next improvements

- Add cached API responses for reproducible demos.
- Save historical snapshots to see how signals change over time.
- Add sector-relative ranking, so a company is compared against its actual peer group instead of the full market.
