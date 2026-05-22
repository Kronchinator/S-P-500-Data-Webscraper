from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests


class StockOracleClient:
    BASE_API = "https://api.stockoracle.com/api"

    def __init__(self, bearer_token: str, timezone: str = "Asia/Singapore") -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "accept": "application/json, text/plain, */*",
                "authorization": f"Bearer {bearer_token}",
                "origin": "https://app.stockoracle.com",
                "referer": "https://app.stockoracle.com/",
                "time-zone": timezone,
                "user-agent": "Mozilla/5.0 (OpenClaw StockOracle Scraper)",
            }
        )

    @classmethod
    def from_credentials_file(cls, path: str | Path) -> "StockOracleClient":
        data = json.loads(Path(path).read_text())
        token = data["stockoracle_bearer_token"].strip()
        return cls(token)

    def _get(self, path: str, **kwargs: Any) -> dict[str, Any]:
        response = self.session.get(f"{self.BASE_API}{path}", timeout=30, **kwargs)
        response.raise_for_status()
        return response.json()

    def _post(self, path: str, **kwargs: Any) -> dict[str, Any]:
        response = self.session.post(f"{self.BASE_API}{path}", timeout=30, **kwargs)
        response.raise_for_status()
        return response.json()

    def get_symbol_detail(self, symbol: str) -> dict[str, Any]:
        payload = self._get("/stock-symbol/get-symbol-detail", params={"symbol": symbol})
        result = payload.get("result")
        if not result:
            raise ValueError(f"No StockOracle symbol detail found for {symbol}")
        if isinstance(result, list):
            return result[0]
        return result

    def get_pagi6(self, stock_id: int) -> dict[str, Any]:
        payload = self._post(f"/stock-detail/pagi6/{stock_id}")
        return payload["result"]

    def get_dcf_20(self, stock_guid: str) -> dict[str, Any]:
        payload = self._get(f"/stock-detail-intrinsic/get-dcf-automation/{stock_guid}")
        return payload["result"]

    def get_oracle_value(self, stock_guid: str) -> dict[str, Any]:
        payload = self._get(f"/stock-detail-intrinsic/get-pp-automation/{stock_guid}")
        return payload["result"]
