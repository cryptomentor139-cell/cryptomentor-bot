from dataclasses import dataclass


@dataclass(frozen=True)
class DecisionThresholds:
    min_confidence_score: float = 0.70
    min_rr_ratio: float = 1.5
    max_spread_bps: float = 10.0


thresholds = DecisionThresholds()
