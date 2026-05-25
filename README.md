# StockOracle Sector Dashboard

This project pulls StockOracle summary data for stocks held in the 11 SPDR sector ETFs. Effectively, the S&P500:

- XLK
- XLF
- XLE
- XLV
- XLY
- XLP
- XLI
- XLB
- XLRE
- XLC
- XLU

## What it fetches

For each ticker, it fetches and derives:

- Oracle Value
- DCF Value
- DCF upside
- Quality score
- Opportunity score
- Signal bucket: Core candidate, Watchlist, Speculative, Neutral, or Avoid / expensive
- Profitability
- Financial Strength
- Oracle Moat
- Valuation

## Data sources

### SSGA holdings
Each ETF page contains a daily holdings workbook link. The script downloads the workbook and extracts tickers.

### StockOracle
The scraper uses three discovered endpoints:

- `GET /api/stock-symbol/get-symbol-detail?symbol={ticker}`
- `POST /api/stock-detail/pagi6/{stockId}`
- `GET /api/stock-detail-intrinsic/get-dcf-automation/{stockGuid}`
- `GET /api/stock-detail-intrinsic/get-pp-automation/{stockGuid}`

## Setup

1. Create a credentials file:

```bash
cp config/credentials.example.json config/credentials.json
```

2. Paste your StockOracle bearer token into `config/credentials.json`.

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

Build dataset:

```bash
python src/build_dataset.py
```

Build dashboard:

```bash
python src/build_dashboard.py
```

Run tests:

```bash
python -m pytest -q
```

Then open:

- `dashboard/index.html`

## Output files

- `data/raw/*.json` raw StockOracle responses per ticker
- `data/processed/stockoracle_sector_dataset.json`
- `data/processed/stockoracle_sector_dataset.csv`
- `data/processed/failures.json`
- `dashboard/index.html`

## Security

Bearer token is rotated frequently, once every 90 mins so this will have to be updated daily. You do need a subsciption for authentication to the StockOracle endpoints.
