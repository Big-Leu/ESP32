"""CRUD operations for sensor readings and ESP32 data."""
from datetime import datetime
from typing import List, Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.db.models.sensor import SensorReading
from Backend.services.esp32.alert_service import (
    AlertService,
    NotificationService,
)
from Backend.services.esp32.predictor import ThresholdPredictor
from Backend.settings import settings
from Backend.web.api.esp32.schema import ReadingCreate


class ESP32Service:
    """Service class for handling ESP32 sensor operations."""

    def __init__(
        self,
        session: AsyncSession,
        predictor: Optional[ThresholdPredictor] = None,
        alert_service: Optional[AlertService] = None,
    ):
        """
        Initialize ESP32 service.

        :param session: Async database session.
        :param predictor: ML predictor instance.
        :param alert_service: Alert service instance.
        """
        self.session = session
        self.predictor = predictor or ThresholdPredictor()

        # Initialize alert service with notification service
        if alert_service is None:
            notification_service = NotificationService()
            self.alert_service = AlertService(
                notification_service=notification_service,
                sustain_seconds=settings.sustain_seconds,
            )
        else:
            self.alert_service = alert_service

        logger.info("ESP32Service initialized")

    async def create_reading(
        self,
        reading_data: ReadingCreate,
    ) -> SensorReading:
        """
        Create a new sensor reading in the database.

        :param reading_data: Sensor reading data.
        :return: Created sensor reading.
        """
        reading = SensorReading(
            ammonia_ppm=reading_data.ammonia_ppm,
            h2s_ppm=reading_data.h2s_ppm,
            temperature=reading_data.temperature,
            humidity=reading_data.humidity,
            created_at=datetime.now(),
        )

        self.session.add(reading)
        await self.session.commit()
        await self.session.refresh(reading)

        logger.info(f"Created sensor reading ID: {reading.id}")
        return reading

    async def get_reading_by_id(
        self,
        reading_id: int,
    ) -> Optional[SensorReading]:
        """
        Get sensor reading by ID.

        :param reading_id: Reading ID.
        :return: Sensor reading or None.
        """
        result = await self.session.execute(
            select(SensorReading).where(SensorReading.id == reading_id),
        )
        return result.scalar_one_or_none()

    async def get_all_readings(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[SensorReading]:
        """
        Get all sensor readings with pagination.

        :param limit: Maximum number of readings to return.
        :param offset: Number of readings to skip.
        :return: List of sensor readings.
        """
        result = await self.session.execute(
            select(SensorReading)
            .order_by(SensorReading.created_at.desc())
            .limit(limit)
            .offset(offset),
        )
        return list(result.scalars().all())

    async def evaluate_alert(
        self,
        reading: SensorReading,
    ) -> dict:
        """
        Evaluate alert conditions for a sensor reading.

        :param reading: Sensor reading to evaluate.
        :return: Alert evaluation result.
        """
        # Get predicted thresholds based on environmental conditions
        thresholds = self.predictor.predict_thresholds(
            temperature=reading.temperature,
            humidity=reading.humidity,
        )

        # Compute fused odor score from current readings
        fused_score = self.predictor.compute_fused_score(
            ammonia_ppm=reading.ammonia_ppm,
            h2s_ppm=reading.h2s_ppm,
        )

        # Check for sustained alert condition using current time
        alert = self.alert_service.check_sustained_alert(
            fused_score=fused_score,
            threshold_moderate=thresholds["score_moderate"],
            threshold_strong=thresholds["score_strong"],
            timestamp=datetime.now(),
        )

        # Send notifications if alert triggered
        if alert:
            self.alert_service.send_alert_notifications(
                alert=alert,
                ammonia_ppm=reading.ammonia_ppm,
                h2s_ppm=reading.h2s_ppm,
            )

            return {
                "alert": True,
                "level": alert["level"],
                "message": alert["message"],
                "score": fused_score,
                "thresholds": thresholds,
            }

        return {
            "alert": False,
            "level": 1,
            "message": "Normal conditions",
            "score": fused_score,
            "thresholds": thresholds,
        }


