"""Pydantic schemas for ESP32 sensor API."""
from datetime import datetime

from pydantic import BaseModel, Field


class Threshold(BaseModel):
    """Threshold values for a single gas."""

    baseline: float = Field(..., description="Baseline threshold value")
    warning: float = Field(..., description="Warning threshold value")
    critical: float = Field(..., description="Critical threshold value")

    class Config:
        """Pydantic config."""

        from_attributes = True


class ThresholdResponse(BaseModel):
    """Response containing thresholds for multiple gases."""

    ammonia: Threshold = Field(..., description="Ammonia thresholds")
    h2s: Threshold = Field(..., description="H2S thresholds")

    class Config:
        """Pydantic config."""

        from_attributes = True


class ReadingCreate(BaseModel):
    """Schema for creating a new sensor reading."""

    ammonia_ppm: float = Field(
        ...,
        ge=0,
        description="Ammonia level in parts per million",
    )
    h2s_ppm: float = Field(
        ...,
        ge=0,
        description="Hydrogen sulfide level in parts per million",
    )
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: float = Field(
        ...,
        ge=0,
        le=100,
        description="Relative humidity percentage",
    )

    class Config:
        """Pydantic config."""

        from_attributes = True


class Reading(BaseModel):
    """Schema for sensor reading response."""

    id: int = Field(..., description="Unique reading ID")
    ammonia_ppm: float = Field(..., description="Ammonia level in ppm")
    h2s_ppm: float = Field(..., description="H2S level in ppm")
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: float = Field(..., description="Relative humidity percentage")
    created_at: datetime = Field(..., description="Timestamp of reading")

    class Config:
        """Pydantic config."""

        from_attributes = True


class PredictRequest(BaseModel):
    """Request schema for threshold prediction."""

    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: float = Field(
        ...,
        ge=0,
        le=100,
        description="Relative humidity percentage",
    )

    class Config:
        """Pydantic config."""

        from_attributes = True


class PredictResponse(BaseModel):
    """Response schema for threshold prediction."""

    baseline_fused: float = Field(
        ...,
        description="Fused baseline odor score (0-100)",
    )
    score_moderate: float = Field(
        ...,
        description="Moderate alert threshold (0-100)",
    )
    score_strong: float = Field(
        ...,
        description="Strong alert threshold (0-100)",
    )

    class Config:
        """Pydantic config."""

        from_attributes = True


class AlertEvaluationResponse(BaseModel):
    """Response schema for alert evaluation."""

    alert: bool = Field(..., description="Whether alert is active")
    level: int = Field(
        ...,
        description="Alert level (1=normal, 2=moderate, 3=strong)",
    )
    message: str = Field(..., description="Alert message")
    score: float = Field(..., description="Current fused odor score")
    thresholds: PredictResponse = Field(
        ...,
        description="Predicted thresholds",
    )

    class Config:
        """Pydantic config."""

        from_attributes = True
