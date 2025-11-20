from storage.chat_repository import storage
from helpers.logger import get_logger

logger = get_logger()


async def send_random_reminder(chat_id: int, application):
    random_message = storage.get_random_message(chat_id)
    
    if not random_message:
        reminder_text = "📭 No messages available yet! Send me some messages to get reminders."
        log_message = "Sent 'no messages' notification"
    else:
        reminder_text = f'💭 **Random Reminder**\n\n"{random_message}"'
        log_message = "Sent reminder"

    try:
        await application.bot.send_message(
            chat_id=chat_id,
            text=reminder_text,
            parse_mode='Markdown'
        )
        logger.info(f"{log_message} to chat {chat_id}")
    except Exception as e:
        logger.error(f"Error sending message to chat {chat_id}: {e}")
