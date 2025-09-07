"""Time utility functions for the Random Reminder Bot."""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def is_notification_time(current_time: datetime, notification_time_str: str, last_datetime: datetime = None) -> bool:
    """Check if we should send a notification now - i.e., if we haven't sent one after notification_time today."""
    try:
        # Parse notification time (format: "HH:MM")
        target_hour, target_minute = map(int, notification_time_str.split(':'))
        
        # Create today's notification time
        today_notification = current_time.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        
        # If current time is before today's notification time, it's not time yet
        if current_time < today_notification:
            return False
        
        # If no last reminder, and we're past notification time, it's time to send
        if last_datetime is None:
            return True
        
        # Check if last reminder was sent before today's notification time
        # If yes, then we haven't sent one after notification time today, so it's time
        return last_datetime < today_notification
        
    except Exception as e:
        logger.error(f"Error checking notification time: {e}")
        return True  # If there's an error, allow sending (fail safe)


def format_interval_display(interval_days: float) -> str:
    if interval_days == 1:
        return "1 day"
    else:
        return f"{interval_days:.0f} days" if interval_days.is_integer() else f"{interval_days} days"
