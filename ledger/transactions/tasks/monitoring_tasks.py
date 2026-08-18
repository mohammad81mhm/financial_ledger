import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def notify_monitoring_team(*, transaction_id: str) -> None:
    """Notify the monitoring team about a high-value transfer.

    Args:
        transaction_id (str): UUID string of the completed transfer transaction.
    """
    logger.warning("High-value transfer alert: transaction_id=%s", transaction_id)
