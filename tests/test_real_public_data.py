from rt_cinfer_web.data.public_web_vitals import PageSpeedCrUXClient
from rt_cinfer_web.data.real_observational import summarize_public_vitals
import pandas as pd


def test_pagespeed_normalization_handles_crux_payload():
    payload = {
        "analysisUTCTimestamp": "2026-07-01T00:00:00Z",
        "loadingExperience": {
            "formFactor": "PHONE",
            "overall_category": "AVERAGE",
            "metrics": {
                "LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 2800, "category": "AVERAGE"},
                "INTERACTION_TO_NEXT_PAINT": {"percentile": 180, "category": "FAST"},
                "CUMULATIVE_LAYOUT_SHIFT_SCORE": {"percentile": 0.08, "category": "FAST"},
            },
        },
        "lighthouseResult": {"categories": {"performance": {"score": 0.82}}},
    }
    record = PageSpeedCrUXClient().normalize(
        "https://example.com", "mobile", payload, "https://example.test/api"
    )
    row = record.as_dict()
    assert row["origin"] == "https://example.com"
    assert row["lcp_p75_ms"] == 2800.0
    assert row["inp_p75_ms"] == 180.0
    assert row["cls_p75"] == 0.08
    assert row["lighthouse_performance_score"] == 0.82


def test_public_observational_summary_reports_boundary():
    df = pd.DataFrame(
        {
            "origin": ["https://a.test", "https://b.test"],
            "lcp_p75_ms": [2100, 3600],
            "inp_p75_ms": [120, 240],
            "cls_p75": [0.05, 0.18],
        }
    )
    summary = summarize_public_vitals(df)
    assert summary.n_rows == 2
    assert summary.n_origins == 2
    assert "should not be described" in summary.identifiability_note
    assert "lcp_p75_ms" in summary.metric_summary
