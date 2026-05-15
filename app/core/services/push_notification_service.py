import logging

logger = logging.getLogger(__name__)


class PushNotificationService:
    """Service for sending push notifications."""

    def send_push_notification(
        self,
        *,
        device_tokens: list[str],
        title: str,
        body: str,
        data: dict | None = None,
    ) -> None:
        """Send a push notification.

        This is currently a placeholder implementation until a push provider is
        integrated.
        """
        logger.info(
            "Push notification placeholder invoked for %s device(s). Title=%s Data=%s Body=%s",
            len(device_tokens),
            title,
            data or {},
            body,
        )
