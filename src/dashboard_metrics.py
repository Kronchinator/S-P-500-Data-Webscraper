from __future__ import annotations

from copy import deepcopy
from statistics import mean
from typing import Any

QUALITY_POINTS = {
    "HIGH": 100,
    "MEDIUM": 50,
    "LOW": 0,
}

MOAT_POINTS = {
    "WIDE": 100,
    "NARROW": 50,
    "NO_MOAT": 0,
}

VALUATION_POINTS = {
    "VERY_UNDERVALUED": 100,
    "UNDERVALUED": 85,
    "FAIRLY_VALUED": 50,
    "OVERVALUED": 15,
    "VERY_OVERVALUED": 0,
}


def _to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _clamp(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))


def _quality_score(row: dict[str, Any]) -> int:
    parts = [
        QUALITY_POINTS.get(str(row.get("profitability") or "").upper(), 0),
        QUALITY_POINTS.get(str(row.get("financial_strength") or "").upper(), 0),
        MOAT_POINTS.get(str(row.get("oracle_moat") or "").upper(), 0),
    ]
    return round(mean(parts))


def _opportunity_score(quality_score: int, valuation: str | None, upside: float | None) -> int:
    valuation_score = VALUATION_POINTS.get(str(valuation or "").upper(), 0)
    upside_score = _clamp(upside or 0)
    score = (quality_score * 0.426) + (valuation_score * 0.444) + (upside_score * 0.13)
    return round(_clamp(score))


def _signal(quality_score: int, opportunity_score: int, upside: float | None) -> str:
    if quality_score >= 80 and opportunity_score >= 70:
        return "Core candidate"
    if opportunity_score >= 65 and (upside or 0) > 0:
        return "Watchlist"
    if quality_score < 35 and (upside or 0) >= 40:
        return "Speculative"
    if opportunity_score < 35:
        return "Avoid / expensive"
    return "Neutral"


def enrich_row(row: dict[str, Any]) -> dict[str, Any]:
    enriched = deepcopy(row)
    oracle_value = _to_float(enriched.get("oracle_value"))
    dcf_value = _to_float(enriched.get("dcf_value"))
    upside = None
    if oracle_value and dcf_value is not None:
        upside = round(((dcf_value - oracle_value) / oracle_value) * 100, 2)

    etf_weights = enriched.get("etf_weights") or {}
    if isinstance(etf_weights, dict) and etf_weights:
        primary_etf, largest_weight = max(etf_weights.items(), key=lambda item: _to_float(item[1]) or 0)
        largest_weight = _to_float(largest_weight) or 0
    else:
        etfs = [part.strip() for part in str(enriched.get("etfs") or "").split(",") if part.strip()]
        primary_etf = etfs[0] if etfs else ""
        largest_weight = 0

    quality_score = _quality_score(enriched)
    opportunity_score = _opportunity_score(quality_score, enriched.get("valuation"), upside)

    enriched.update(
        {
            "oracle_value_num": oracle_value,
            "dcf_value_num": dcf_value,
            "upside": upside,
            "quality_score": quality_score,
            "opportunity_score": opportunity_score,
            "signal": _signal(quality_score, opportunity_score, upside),
            "primary_etf": primary_etf,
            "largest_etf_weight": round(largest_weight, 4),
        }
    )
    return enriched


def summarize_sector(etf: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {
            "etf": etf,
            "stocks": 0,
            "avg_upside": 0,
            "wide_moat": 0,
            "undervalued": 0,
            "core_candidates": 0,
            "avg_opportunity_score": 0,
        }

    upsides = [float(row["upside"]) for row in rows if row.get("upside") is not None]
    scores = [float(row["opportunity_score"]) for row in rows if row.get("opportunity_score") is not None]
    return {
        "etf": etf,
        "stocks": len(rows),
        "avg_upside": round(mean(upsides), 2) if upsides else 0,
        "wide_moat": sum(1 for row in rows if row.get("oracle_moat") == "WIDE"),
        "undervalued": sum(1 for row in rows if row.get("valuation") in {"UNDERVALUED", "VERY_UNDERVALUED"}),
        "core_candidates": sum(1 for row in rows if row.get("signal") == "Core candidate"),
        "avg_opportunity_score": round(mean(scores)) if scores else 0,
    }


def rank_opportunities(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (row.get("opportunity_score") or 0, row.get("upside") or 0),
        reverse=True,
    )


def enrich_dataset(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [enrich_row(row) for row in rows]
