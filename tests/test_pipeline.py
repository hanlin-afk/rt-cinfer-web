from rt_cinfer_web.data.synthetic import SyntheticWebVitalsStream
from rt_cinfer_web.pipeline import PipelineConfig, RealTimeCausalPipeline


def test_pipeline_report_contains_required_sections():
    stream = SyntheticWebVitalsStream(seed=8, drift_at=1000)
    pipeline = RealTimeCausalPipeline(PipelineConfig(metric="lcp_ms"))
    report = None
    for batch in stream.iter_batches(n_events=1500, batch_size=300):
        report = pipeline.update(batch)
    assert report is not None
    data = report.as_dict()
    assert "estimate" in data
    assert "recommendations" in data
    assert "bottlenecks" in data
    assert data["counterfactual"] is not None
