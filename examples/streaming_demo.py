from rt_cinfer_web.data.synthetic import SyntheticWebVitalsStream
from rt_cinfer_web.pipeline import PipelineConfig, RealTimeCausalPipeline

stream = SyntheticWebVitalsStream(seed=21, drift_at=3000)
pipeline = RealTimeCausalPipeline(PipelineConfig(metric="lcp_ms"))

for step, batch in enumerate(stream.iter_batches(n_events=6000, batch_size=300), start=1):
    report = pipeline.update(batch)
    if step % 5 == 0:
        est = report.estimate
        print(
            f"batch={step:02d} n={est.n} ate={est.ate:.1f} "
            f"ci=[{est.ci_low:.1f}, {est.ci_high:.1f}] drift={report.drift_flags}"
        )
