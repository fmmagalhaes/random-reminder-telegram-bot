"""Time utility functions for the Random Reminder Bot."""

import logging
from datetime import datetime, timedelta
from typing import Optional
from croniter import croniter

logger = logging.getLogger(__name__)


def should_trigger_cron(cron_expression: str, last_reminder: Optional[datetime] = None) -> bool:
    try:
        current_time = datetime.now()
        
        # If no last reminder, check if we're at a cron time right now
        if last_reminder is None:
            cron = croniter(cron_expression, current_time)
            prev_time = cron.get_prev(datetime)
            
            # If the previous occurrence was within the last minute, trigger
            return current_time - prev_time <= timedelta(minutes=1)
        
        # If we have a last reminder time, check if next scheduled time has passed
        cron = croniter(cron_expression, last_reminder)
        next_time = cron.get_next(datetime)
        
        return current_time >= next_time
        
    except ValueError as e:
        logger.error(f"Invalid cron expression '{cron_expression}': {e}")
        return False
    except Exception as e:
        logger.error(f"Error checking cron trigger for '{cron_expression}': {e}")
        return False



