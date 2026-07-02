from rt_cinfer_web.data.synthetic import SyntheticWebVitalsStream
from rt_cinfer_web.pipeline import PipelineConfig, RealTimeCausalPipeline

stream = SyntheticWebVitalsStream(seed=7)
pipeline = RealTimeCausalPipeline(PipelineConfig(metric="lcp_ms", treatment="edge_cache_enabled"))

report = None
for batch in stream.iter_batches(n_events=5000, batch_size=250):
    report = pipeline.update(batch)

assert report is not None
print("Final estimate:", report.estimate.as_dict())
print("Top bottlenecks:", report.bottlenecks)
print("Recommendation:", report.recommendations[0].as_dict())
