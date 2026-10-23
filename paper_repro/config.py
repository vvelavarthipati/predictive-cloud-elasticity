"""Configuration for the published-paper reproducibility experiment."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ExperimentConfig:
    minutes_per_step: int = 5
    days: int = 7
    forecast_horizon_minutes: int = 15
    target_utilization: float = 0.90
    reactive_actuation_minutes: int = 15
    predictive_actuation_minutes: int = 5
    seeds: tuple = (11, 22, 33)
    train_fraction: float = 0.60
    calibration_fraction: float = 0.20
    confidence_threshold: float = 0.20
    ood_threshold: float = 3.0
    xgboost_estimators: int = 100
    xgboost_max_depth: int = 4
    xgboost_learning_rate: float = 0.05

    @property
    def samples_per_day(self):
        return (24 * 60) // self.minutes_per_step

    @property
    def samples(self):
        return self.samples_per_day * self.days

    @property
    def horizon_steps(self):
        if self.forecast_horizon_minutes % self.minutes_per_step:
            raise ValueError("forecast horizon must be a multiple of the telemetry interval")
        return self.forecast_horizon_minutes // self.minutes_per_step

    @property
    def reactive_delay_steps(self):
        if self.reactive_actuation_minutes % self.minutes_per_step:
            raise ValueError("reactive actuation delay must be a multiple of the telemetry interval")
        return self.reactive_actuation_minutes // self.minutes_per_step

    @property
    def predictive_delay_steps(self):
        if self.predictive_actuation_minutes % self.minutes_per_step:
            raise ValueError("predictive actuation delay must be a multiple of the telemetry interval")
        return self.predictive_actuation_minutes // self.minutes_per_step

    def validate(self):
        if self.minutes_per_step <= 0 or self.days <= 0:
            raise ValueError("telemetry interval and duration must be positive")
        if not 0 < self.target_utilization <= 1:
            raise ValueError("target utilization must be in (0, 1]")
        if not 0 < self.train_fraction < 1:
            raise ValueError("train_fraction must be in (0, 1)")
        if not 0 < self.calibration_fraction < 1:
            raise ValueError("calibration_fraction must be in (0, 1)")
        if self.train_fraction + self.calibration_fraction >= 1:
            raise ValueError("training and calibration fractions must leave a test set")
        if not self.seeds:
            raise ValueError("at least one random seed is required")
        _ = self.horizon_steps
        _ = self.reactive_delay_steps
        _ = self.predictive_delay_steps
        return self
