"""Sensor reading database model."""
from sqlalchemy import Column, DateTime, Float, Integer
from sqlalchemy.sql import func

from Backend.db.base import Base


class SensorReading(Base):
    """Model for storing ESP32 sensor readings."""

    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    ammonia_ppm = Column(Float, nullable=False, comment="Ammonia level in ppm")
    h2s_ppm = Column(Float, nullable=False, comment="H2S level in ppm")
    temperature = Column(
        Float,
        nullable=False,
        comment="Temperature in Celsius",
    )
    humidity = Column(
        Float,
        nullable=False,
        comment="Relative humidity percentage",
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="Timestamp of reading",
    )

    def __repr__(self) -> str:
        """String representation of sensor reading."""
        return (
            f"<SensorReading(id={self.id}, "
            f"NH3={self.ammonia_ppm:.2f}, "
            f"H2S={self.h2s_ppm:.2f}, "
            f"temp={self.temperature:.1f}°C, "
            f"humidity={self.humidity:.1f}%)>"
        )
