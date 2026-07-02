import pytest

from rt_cinfer_web.scm.graph import CausalGraph, default_web_vitals_graph
from rt_cinfer_web.scm.identifiability import backdoor_adjustment_check
from rt_cinfer_web.config import FeatureSchema


def test_graph_rejects_cycle():
    g = CausalGraph()
    g.add_edge("a", "b")
    g.add_edge("b", "c")
    with pytest.raises(ValueError):
        g.add_edge("c", "a")


def test_default_graph_identifiable_with_schema():
    schema = FeatureSchema()
    g = default_web_vitals_graph()
    result = backdoor_adjustment_check(
        g, treatment=schema.treatment, outcome=schema.outcome, observed_covariates=schema.context_features
    )
    assert result.identifiable
    assert "network_rtt_ms" in result.adjustment_set
