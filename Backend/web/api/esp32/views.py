"""API endpoints for ESP32 sensor readings and alerts."""
from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.db.dependencies import get_db_session
from Backend.db.models.users import User, current_active_user
from Backend.services.esp32.crud import ESP32Service
from Backend.services.esp32.predictor import ThresholdPredictor
from Backend.web.api.esp32.schema import (
    AlertEvaluationResponse,
    PredictRequest,
    PredictResponse,
    Reading,
    ReadingCreate,
)

router = APIRouter()

# Singleton instances (loaded once and shared across requests)
_predictor = ThresholdPredictor()
_notification_service = None
_alert_service = None


def get_alert_service():
    """Get or create singleton alert service."""
    global _notification_service, _alert_service
    
    if _alert_service is None:
        from Backend.services.esp32.alert_service import (
            AlertService,
            NotificationService,
        )
        from Backend.settings import settings
        
        _notification_service = NotificationService()
        _alert_service = AlertService(
            notification_service=_notification_service,
            sustain_seconds=settings.sustain_seconds,
        )
    
    return _alert_service


def get_esp32_service(
    db: AsyncSession = Depends(get_db_session),
) -> ESP32Service:
    """
    Get ESP32 service instance.

    :param db: Database session.
    :return: ESP32Service instance.
    """
    alert_service = get_alert_service()
    return ESP32Service(
        session=db,
        predictor=_predictor,
        alert_service=alert_service,
    )


@router.post("/readings", response_model=Reading, status_code=201)
async def create_reading(
    reading_data: ReadingCreate,
    service: ESP32Service = Depends(get_esp32_service),
    user: User = Depends(current_active_user),
) -> Reading:
    """
    Create a new sensor reading from ESP32 device.

    :param reading_data: Sensor reading data.
    :param service: ESP32 service instance.
    :param user: Current authenticated user.
    :return: Created sensor reading.
    """
    logger.info(f"User {user.id} creating sensor reading")

    # Create reading in database
    reading = await service.create_reading(reading_data)

    # Evaluate alert condition (non-blocking)
    try:
        await service.evaluate_alert(reading)
    except Exception as e:
        logger.error(f"Alert evaluation failed: {e}")
        # Don't fail the request if alert evaluation fails

    return reading


@router.get("/readings", response_model=Sequence[Reading])
async def get_readings(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    service: ESP32Service = Depends(get_esp32_service),
    user: User = Depends(current_active_user),
) -> Sequence[Reading]:
    """
    Get sensor readings with pagination.

    :param limit: Maximum number of readings to return.
    :param offset: Number of readings to skip.
    :param service: ESP32 service instance.
    :param user: Current authenticated user.
    :return: List of sensor readings.
    """
    logger.info(
        f"User {user.id} retrieving readings (limit={limit}, offset={offset})",
    )
    readings = await service.get_all_readings(limit=limit, offset=offset)
    return readings


@router.get("/readings/{reading_id}", response_model=Reading)
async def get_reading(
    reading_id: int,
    service: ESP32Service = Depends(get_esp32_service),
    user: User = Depends(current_active_user),
) -> Reading:
    """
    Get a specific sensor reading by ID.

    :param reading_id: Reading ID.
    :param service: ESP32 service instance.
    :param user: Current authenticated user.
    :return: Sensor reading.
    """
    logger.info(f"User {user.id} retrieving reading {reading_id}")
    reading = await service.get_reading_by_id(reading_id)

    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found")

    return reading


@router.post("/predict", response_model=PredictResponse)
async def predict_thresholds(
    request: PredictRequest,
    user: User = Depends(current_active_user),
) -> PredictResponse:
    """
    Predict odor thresholds based on environmental conditions.

    :param request: Temperature and humidity data.
    :param user: Current authenticated user.
    :return: Predicted thresholds.
    """
    logger.info(
        f"User {user.id} requesting threshold prediction "
        f"(temp={request.temperature}, humidity={request.humidity})",
    )

    thresholds = _predictor.predict_thresholds(
        temperature=request.temperature,
        humidity=request.humidity,
    )

    return PredictResponse(**thresholds)


@router.post(
    "/alerts/evaluate/{reading_id}",
    response_model=AlertEvaluationResponse,
)
async def evaluate_alert(
    reading_id: int,
    service: ESP32Service = Depends(get_esp32_service),
    user: User = Depends(current_active_user),
) -> AlertEvaluationResponse:
    """
    Evaluate alert conditions for a specific reading.

    :param reading_id: Reading ID to evaluate.
    :param service: ESP32 service instance.
    :param user: Current authenticated user.
    :return: Alert evaluation result.
    """
    logger.info(f"User {user.id} evaluating alert for reading {reading_id}")

    # Get the reading
    reading = await service.get_reading_by_id(reading_id)
    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found")

    # Evaluate alert
    result = await service.evaluate_alert(reading)

    return AlertEvaluationResponse(**result)
