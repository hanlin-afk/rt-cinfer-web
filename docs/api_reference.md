# API Reference

## `SyntheticWebVitalsStream`

Generates deterministic synthetic events with confounded intervention assignment and known ground-truth effects.

```python
from rt_cinfer_web.data.synthetic import SyntheticWebVitalsStream

df = SyntheticWebVitalsStream(seed=7).generate(n_events=1000)
```

## `OnlineDoublyRobustEstimator`

Processes streaming batches and estimates an average treatment effect.

```python
from rt_cinfer_web.estimators.online_dr import OnlineDoublyRobustEstimator
from rt_cinfer_web.config import FeatureSchema

schema = FeatureSchema()
estimator = OnlineDoublyRobustEstimator(
    features=schema.context_features,
    treatment="edge_cache_enabled",
    outcome="lcp_ms",
)
estimate = estimator.update(batch)
```

## `RealTimeCausalPipeline`

Runs the full stack: identifiability check, online DR estimation, drift detection, bottleneck localization, counterfactual simulation, and recommendation gating.

```python
from rt_cinfer_web.pipeline import RealTimeCausalPipeline, PipelineConfig

pipeline = RealTimeCausalPipeline(PipelineConfig(metric="lcp_ms"))
report = pipeline.update(batch)
print(report.as_dict())
```

## CLI

```bash
rt-cinfer-web generate --n-events 1000 --output data/samples/synthetic.csv
rt-cinfer-web benchmark --n-events 5000 --seed 7
```
