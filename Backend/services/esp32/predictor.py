"""ML prediction service for gas threshold detection."""
import os
import pickle
from pathlib import Path
from typing import Dict

import pandas as pd
from loguru import logger


class ThresholdPredictor:
    """Handles ML-based threshold prediction for gas sensors."""

    def __init__(self, model_path: str | None = None):
        """
        Initialize the predictor with a trained Ridge model.

        :param model_path: Path to the pickled model file.
        """
        if model_path is None:
            model_path = os.path.join(
                os.path.dirname(__file__),
                "model.pkl",
            )

        self.model_path = Path(model_path)
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        """Load the Ridge regression model from disk."""
        try:
            with open(self.model_path, "rb") as f:
                self.model = pickle.load(f)
            logger.info(f"ML model loaded successfully from {self.model_path}")
        except FileNotFoundError:
            logger.error(f"Model file not found at {self.model_path}")
            raise
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    @staticmethod
    def normalize(value: float, max_value: float) -> float:
        """
        Normalize sensor reading to 0-100 scale.

        :param value: Raw sensor value.
        :param max_value: Maximum expected value for the sensor.
        :return: Normalized value (0-100).
        """
        if value <= 0:
            return 0.0
        if value >= max_value:
            return 100.0
        return (value / max_value) * 100.0

    def predict_thresholds(
        self,
        temperature: float,
        humidity: float,
    ) -> Dict[str, float]:
        """
        Predict odor thresholds based on temperature and humidity.

        :param temperature: Temperature in Celsius.
        :param humidity: Relative humidity percentage.
        :return: Dictionary with baseline, moderate, and strong thresholds.
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")

        # Prepare input data
        df = pd.DataFrame({
            "temperature": [temperature],
            "humidity": [humidity],
        })

        # Ridge model predicts (baseline_nh3, baseline_h2s)
        baseline_nh3, baseline_h2s = self.model.predict(df)[0]

        logger.debug(
            f"Predicted baselines - NH3: {baseline_nh3:.3f}, "
            f"H2S: {baseline_h2s:.3f}",
        )

        # Normalize to 0-100 smell intensity
        # NH₃ max ~ 5 ppm
        norm_nh3 = self.normalize(baseline_nh3, max_value=5.0)
        # H₂S max ~ 0.1 ppm
        norm_h2s = self.normalize(baseline_h2s, max_value=0.1)

        # Fused odour baseline (weighted average)
        fused_baseline = (norm_nh3 * 0.5) + (norm_h2s * 0.5)

        # Calculate fused thresholds
        score_moderate = min(100.0, fused_baseline * 1.5)
        score_strong = min(100.0, fused_baseline * 2.0)

        return {
            "baseline_fused": round(fused_baseline, 2),
            "score_moderate": round(score_moderate, 2),
            "score_strong": round(score_strong, 2),
        }

    def compute_fused_score(self, ammonia_ppm: float, h2s_ppm: float) -> float:
        """
        Compute fused odor score from current sensor readings.

        :param ammonia_ppm: Current ammonia level in ppm.
        :param h2s_ppm: Current H2S level in ppm.
        :return: Fused score (0-100).
        """
        norm_nh3 = self.normalize(ammonia_ppm, max_value=5.0)
        norm_h2s = self.normalize(h2s_ppm, max_value=0.1)
        fused_score = (norm_nh3 * 0.5) + (norm_h2s * 0.5)

        logger.debug(
            f"Fused score: {fused_score:.2f} "
            f"(NH3: {ammonia_ppm:.2f} ppm, H2S: {h2s_ppm:.2f} ppm)",
        )

        return round(fused_score, 2)
