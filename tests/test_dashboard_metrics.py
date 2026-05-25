from src.dashboard_metrics import enrich_row, summarize_sector, rank_opportunities


def test_enrich_row_calculates_upside_quality_and_opportunity_score():
    row = {
        "ticker": "ACME",
        "name": "ACME BANK",
        "etfs": "XLF",
        "oracle_value": "100",
        "dcf_value": 130,
        "profitability": "HIGH",
        "financial_strength": "MEDIUM",
        "oracle_moat": "WIDE",
        "valuation": "UNDERVALUED",
        "etf_weights": {"XLF": 2.5},
    }

    enriched = enrich_row(row)

    assert enriched["upside"] == 30.0
    assert enriched["quality_score"] == 83
    assert enriched["opportunity_score"] == 77
    assert enriched["primary_etf"] == "XLF"
    assert enriched["largest_etf_weight"] == 2.5
    assert enriched["signal"] == "Core candidate"


def test_enrich_row_penalizes_low_quality_value_traps():
    row = {
        "ticker": "TRAP",
        "name": "VALUE TRAP INC",
        "etfs": "XLU",
        "oracle_value": "100",
        "dcf_value": 180,
        "profitability": "LOW",
        "financial_strength": "LOW",
        "oracle_moat": "NO_MOAT",
        "valuation": "UNDERVALUED",
        "etf_weights": {"XLU": 0.5},
    }

    enriched = enrich_row(row)

    assert enriched["upside"] == 80.0
    assert enriched["quality_score"] == 0
    assert enriched["opportunity_score"] == 48
    assert enriched["signal"] == "Speculative"


def test_summarize_sector_uses_weighted_opportunity_and_quality_counts():
    rows = [
        enrich_row({"ticker": "A", "name": "A", "etfs": "XLF", "oracle_value": "100", "dcf_value": 120, "profitability": "HIGH", "financial_strength": "HIGH", "oracle_moat": "WIDE", "valuation": "UNDERVALUED", "etf_weights": {"XLF": 2.0}}),
        enrich_row({"ticker": "B", "name": "B", "etfs": "XLF", "oracle_value": "100", "dcf_value": 90, "profitability": "LOW", "financial_strength": "LOW", "oracle_moat": "NO_MOAT", "valuation": "OVERVALUED", "etf_weights": {"XLF": 1.0}}),
    ]

    summary = summarize_sector("XLF", rows)

    assert summary["etf"] == "XLF"
    assert summary["stocks"] == 2
    assert summary["avg_upside"] == 5.0
    assert summary["wide_moat"] == 1
    assert summary["core_candidates"] == 1
    assert summary["avg_opportunity_score"] == 45


def test_rank_opportunities_sorts_by_score_then_upside():
    rows = [
        {"ticker": "LOW", "opportunity_score": 20, "upside": 200},
        {"ticker": "HIGH", "opportunity_score": 90, "upside": 10},
        {"ticker": "TIE", "opportunity_score": 90, "upside": 40},
    ]

    ranked = rank_opportunities(rows)

    assert [row["ticker"] for row in ranked] == ["TIE", "HIGH", "LOW"]
