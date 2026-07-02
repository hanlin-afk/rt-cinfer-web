"""RT-CInfer-Web: streaming causal inference for Web Vitals."""

from rt_cinfer_web.estimators.online_dr import CausalEstimate, OnlineDoublyRobustEstimator
from rt_cinfer_web.pipeline import PipelineConfig, PipelineReport, RealTimeCausalPipeline

__all__ = [
    "CausalEstimate",
    "OnlineDoublyRobustEstimator",
    "PipelineConfig",
    "PipelineReport",
    "RealTimeCausalPipeline",
]

__version__ = "0.1.0"
