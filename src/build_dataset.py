from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from stockoracle_client import StockOracleClient
from ssga_holdings import fetch_all_holdings

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
CONFIG_PATH = ROOT / "config" / "credentials.json"


def rank_value(pagi: dict[str, Any], rank_name: str) -> dict[str, Any] | None:
    for item in pagi.get("pagiRank", []):
        if item.get("name") == rank_name:
            return item
    return None


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    client = StockOracleClient.from_credentials_file(CONFIG_PATH)
    holdings = fetch_all_holdings()

    unique: dict[str, dict[str, Any]] = {}
    for row in holdings:
        unique.setdefault(row["ticker"], row)

    enriched: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    for ticker, row in sorted(unique.items()):
        try:
            symbol_detail = client.get_symbol_detail(ticker)
            stock_id = symbol_detail["id"]
            stock_guid = symbol_detail["stockGuid"]
            pagi = client.get_pagi6(stock_id)
            dcf = client.get_dcf_20(stock_guid)
            oracle_value = client.get_oracle_value(stock_guid)

            profitability = rank_value(pagi, "PROFITABILITY_RANK")
            financial_strength = rank_value(pagi, "FINANCIAL_STRENGTH_RANK")
            moat = rank_value(pagi, "MOAT_RANK")
            valuation = rank_value(pagi, "VALUATION_RANK")

            pp_value = None
            if valuation:
                for detail in valuation.get("details", []):
                    if detail.get("name") == "PP_VALUE":
                        pp_value = detail.get("value")
                        break

            etfs = sorted({h["etf"] for h in holdings if h["ticker"] == ticker})
            weights = {h["etf"]: h.get("weight") for h in holdings if h["ticker"] == ticker}

            enriched.append(
                {
                    "ticker": ticker,
                    "name": row["name"],
                    "etfs": ", ".join(etfs),
                    "stock_id": stock_id,
                    "stock_guid": stock_guid,
                    "oracle_value": pp_value or oracle_value.get("intrinsicValue"),
                    "oracle_value_intrinsic": oracle_value.get("intrinsicValue"),
                    "dcf_value": dcf.get("intrinsicValue"),
                    "profitability": profitability.get("value") if profitability else None,
                    "financial_strength": financial_strength.get("value") if financial_strength else None,
                    "oracle_moat": moat.get("value") if moat else None,
                    "valuation": valuation.get("value") if valuation else None,
                    "etf_weights": weights,
                }
            )

            (RAW_DIR / f"{ticker}.json").write_text(
                json.dumps(
                    {
                        "symbol_detail": symbol_detail,
                        "pagi6": pagi,
                        "dcf_20": dcf,
                        "oracle_value": oracle_value,
                    },
                    indent=2,
                )
            )
        except Exception as exc:
            failures.append({"ticker": ticker, "error": str(exc)})

    (PROCESSED_DIR / "stockoracle_sector_dataset.json").write_text(json.dumps(enriched, indent=2))

    if enriched:
        with (PROCESSED_DIR / "stockoracle_sector_dataset.csv").open("w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "ticker",
                    "name",
                    "etfs",
                    "stock_id",
                    "stock_guid",
                    "oracle_value",
                    "oracle_value_intrinsic",
                    "dcf_value",
                    "profitability",
                    "financial_strength",
                    "oracle_moat",
                    "valuation",
                    "etf_weights",
                ],
            )
            writer.writeheader()
            for row in enriched:
                writer.writerow({**row, "etf_weights": json.dumps(row["etf_weights"])})

    (PROCESSED_DIR / "failures.json").write_text(json.dumps(failures, indent=2))
    print(f"Wrote {len(enriched)} records, {len(failures)} failures")


if __name__ == "__main__":
    main()
