import logging

logger = logging.getLogger(__name__)


class SMSService:
    """Service for sending SMS notifications."""

    def send_sms(self, *, phone_numbers: list[str], message: str, metadata: dict | None = None) -> None:
        """Send an SMS notification.

        This is currently a placeholder implementation until an external SMS
        provider is integrated.
        """
        logger.info(
            "SMS notification placeholder invoked for %s recipient(s). Metadata=%s Message=%s",
            len(phone_numbers),
            metadata or {},
            message,
        )
