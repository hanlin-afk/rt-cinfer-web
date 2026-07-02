"""Instrumental-variable diagnostics for web-performance interventions."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class IVDiagnostic:
    instrument: str
    treatment: str
    outcome: str
    relevance_corr: float
    exclusion_note: str
    passes_relevance: bool


def simple_iv_diagnostic(
    df: pd.DataFrame,
    instrument: str,
    treatment: str,
    outcome: str,
    min_abs_corr: float = 0.05,
    exclusion_note: str = "Exclusion restriction must be justified by design, not by this diagnostic.",
) -> IVDiagnostic:
    """Compute a transparent first-stage relevance diagnostic.

    This function deliberately does not claim to prove the exclusion restriction.
    It only checks whether an instrument is empirically associated with treatment.
    """

    if instrument not in df or treatment not in df or outcome not in df:
        raise ValueError("instrument, treatment, and outcome columns must exist")
    corr = float(np.corrcoef(df[instrument].astype(float), df[treatment].astype(float))[0, 1])
    if not np.isfinite(corr):
        corr = 0.0
    return IVDiagnostic(
        instrument=instrument,
        treatment=treatment,
        outcome=outcome,
        relevance_corr=corr,
        exclusion_note=exclusion_note,
        passes_relevance=abs(corr) >= min_abs_corr,
    )
