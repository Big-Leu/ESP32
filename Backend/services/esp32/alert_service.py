"""Alert service for sustained odor detection and notifications."""
from datetime import datetime
from typing import Any, Dict, Optional

from loguru import logger
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client

from Backend.settings import settings


class AlertLevel:
    """Alert level constants."""

    NORMAL = 1
    MODERATE = 2
    STRONG = 3


class AlertState:
    """Tracks sustained alert state."""

    def __init__(self) -> None:
        """Initialize alert state."""
        self.above_since: Optional[datetime] = None
        self.alert_sent: bool = False
        self.last_level: int = AlertLevel.NORMAL

    def reset(self) -> None:
        """Reset alert state to normal."""
        self.above_since = None
        self.alert_sent = False
        self.last_level = AlertLevel.NORMAL


class NotificationService:
    """Handles SMS and email notifications."""

    def __init__(self) -> None:
        """Initialize notification clients."""
        self.sms_client = None
        self.sendgrid_client = None

        # Initialize Twilio SMS client
        if settings.twilio_sid and settings.twilio_token:
            try:
                self.sms_client = Client(
                    settings.twilio_sid,
                    settings.twilio_token,
                )
                logger.info("Twilio SMS client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")

        # Initialize SendGrid email client
        if settings.sendgrid_api_key:
            try:
                self.sendgrid_client = SendGridAPIClient(
                    settings.sendgrid_api_key,
                )
                logger.info("SendGrid email client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize SendGrid client: {e}")

    def send_sms(self, message: str) -> bool:
        """
        Send SMS notification.

        :param message: Message content.
        :return: True if sent successfully, False otherwise.
        """
        if not self.sms_client:
            logger.warning("SMS client not configured, skipping SMS")
            return False

        if not settings.twilio_phone or not settings.alert_phone:
            logger.warning("Phone numbers not configured, skipping SMS")
            return False

        try:
            response = self.sms_client.messages.create(
                body=message,
                from_=settings.twilio_phone,
                to=settings.alert_phone,
            )
            logger.info(f"SMS sent successfully: {response.sid}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return False

    def send_email(self, subject: str, message: str) -> bool:
        """
        Send email notification.

        :param subject: Email subject.
        :param message: Email body.
        :return: True if sent successfully, False otherwise.
        """
        if not self.sendgrid_client:
            logger.warning("Email client not configured, skipping email")
            return False

        if not settings.from_email or not settings.alert_email:
            logger.warning("Email addresses not configured, skipping email")
            return False

        try:
            mail = Mail(
                from_email=settings.from_email,
                to_emails=settings.alert_email,
                subject=subject,
                plain_text_content=message,
            )
            self.sendgrid_client.send(mail)
            logger.info("Email sent successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False


class AlertService:
    """Service for evaluating sustained odor alerts."""

    def __init__(
        self,
        notification_service: NotificationService,
        sustain_seconds: int,
    ):
        """
        Initialize alert service.

        :param notification_service: Service for sending notifications.
        :param sustain_seconds: Duration for sustained alert condition.
        """
        self.notification_service = notification_service
        self.sustain_seconds = sustain_seconds
        self.alert_state = AlertState()
        logger.info(
            f"AlertService initialized with sustain_seconds={sustain_seconds}",
        )

    def check_sustained_alert(
        self,
        fused_score: float,
        threshold_moderate: float,
        threshold_strong: float,
        timestamp: datetime,
    ) -> Optional[Dict[str, Any]]:
        """
        Check if odor levels exceed thresholds for sustained period.

        :param fused_score: Current fused odor score (0-100).
        :param threshold_moderate: Moderate alert threshold.
        :param threshold_strong: Strong alert threshold.
        :param timestamp: Current timestamp.
        :return: Alert dict if triggered, None otherwise.
        """
        # Determine odor level
        if fused_score >= threshold_strong:
            level = AlertLevel.STRONG
        elif fused_score >= threshold_moderate:
            level = AlertLevel.MODERATE
        else:
            # Below moderate threshold - reset state
            if self.alert_state.above_since is not None:
                logger.info("Odor level returned to normal, resetting alert")
            self.alert_state.reset()
            return None

        # First time crossing threshold
        if self.alert_state.above_since is None:
            self.alert_state.above_since = timestamp
            self.alert_state.last_level = level
            logger.info(
                f"Threshold crossed (Level {level}), "
                f"starting sustain timer at {timestamp}",
            )
            return None

        # Check sustained condition
        elapsed = (timestamp - self.alert_state.above_since).total_seconds()
        logger.debug(
            f"Sustained time: {elapsed:.1f}s / {self.sustain_seconds}s",
        )

        # Trigger alert if sustained and not already sent
        if elapsed >= self.sustain_seconds and not self.alert_state.alert_sent:
            self.alert_state.alert_sent = True
            self.alert_state.last_level = level

            if level == AlertLevel.STRONG:
                message = (
                    f"🚨 Level-3 STRONG Odour! Fused score={fused_score:.2f}. "
                    "Immediate cleaning needed!"
                )
            else:  # MODERATE
                message = (
                    f"⚠️ Level-2 MODERATE odour detected "
                    f"(score={fused_score:.2f}). Please attend soon."
                )

            logger.warning(f"Alert triggered: {message}")

            return {
                "level": level,
                "message": message,
                "score": fused_score,
                "sustained_seconds": elapsed,
            }

        return None

    def send_alert_notifications(
        self,
        alert: Dict[str, Any],
        ammonia_ppm: float,
        h2s_ppm: float,
    ) -> None:
        """
        Send alert notifications via SMS and email.

        :param alert: Alert details from check_sustained_alert.
        :param ammonia_ppm: Current ammonia reading.
        :param h2s_ppm: Current H2S reading.
        """
        full_message = (
            "🚽 Washroom Odour Alert\n\n"
            f"{alert['message']}\n"
            f"NH₃={ammonia_ppm:.2f} ppm, H₂S={h2s_ppm:.2f} ppm\n"
            f"Sustained for {alert['sustained_seconds']:.1f} seconds"
        )

        # Send notifications
        sms_sent = self.notification_service.send_sms(full_message)
        email_sent = self.notification_service.send_email(
            "Washroom Odour Alert",
            full_message,
        )

        logger.info(
            f"Alert notifications sent - SMS: {sms_sent}, Email: {email_sent}",
        )
