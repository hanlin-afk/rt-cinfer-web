from rt_cinfer_web.config import FeatureSchema
from rt_cinfer_web.data.synthetic import SyntheticWebVitalsStream
from rt_cinfer_web.estimators.online_dr import OnlineDoublyRobustEstimator


def test_online_dr_estimator_learns_beneficial_lcp_effect():
    schema = FeatureSchema()
    est = OnlineDoublyRobustEstimator(
        features=schema.context_features,
        treatment="edge_cache_enabled",
        outcome="lcp_ms",
    )
    stream = SyntheticWebVitalsStream(seed=4, drift_at=None)
    result = None
    for batch in stream.iter_batches(n_events=5000, batch_size=250):
        result = est.update(batch)
    assert result is not None
    assert result.n == 5000
    assert result.ate < 0
    assert result.treated_fraction > 0.05
