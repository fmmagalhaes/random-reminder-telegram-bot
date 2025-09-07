from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from storage.message_storage import storage
from helpers.logger import get_logger
from helpers.auth_wrapper import execute_with_authentication
import re

logger = get_logger()

# Conversation states
WAITING_FOR_TIME = 1


@execute_with_authentication()
async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the notification time setting process."""
    chat_id = update.effective_chat.id
    
    current_time = storage.get_chat_notification_time(chat_id)
    
    if current_time:
        time_str = current_time
    else:
        time_str = "not set (will send at any time)"
    
    await update.message.reply_text(
        f"⏰ Current notification time: {time_str}\n\n"
        f"Please send me the time when you want to receive notifications.\n"
        f"Examples:\n"
        f"• 07:00\n"
        f"• 19:45\n\n"
        f"Send /cancel to cancel this operation."
    )
    
    return WAITING_FOR_TIME


@execute_with_authentication()
async def handle_time_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the time input from the user."""
    chat_id = update.effective_chat.id
    time_text = update.message.text.strip().upper()
    
    try:
        # Parse time format like "07:00", "19:45", etc.
        time_pattern = r'^(\d{1,2}):(\d{2})$'
        match = re.match(time_pattern, time_text)
        
        if not match:
            await update.message.reply_text(
                "❌ Invalid time format! Please use 24-hour format like:\n"
                "• 07:00\n"
                "• 19:45\n\n"
                "Send /cancel to cancel this operation."
            )
            return WAITING_FOR_TIME
        
        hour = int(match.group(1))
        minute = int(match.group(2))
        
        # Validate hour and minute for 24-hour format
        if hour < 0 or hour > 23 or minute < 0 or minute > 59:
            await update.message.reply_text(
                "❌ Invalid time! Please use:\n"
                "• Hours between 00-23\n"
                "• Minutes between 00-59\n\n"
                "Send /cancel to cancel this operation."
            )
            return WAITING_FOR_TIME
        
        # Store the time (already in 24-hour format)
        time_str = f"{hour:02d}:{minute:02d}"
        success = storage.set_chat_notification_time(chat_id, time_str)
        
        if success:
            await update.message.reply_text(
                f"✅ Notification time set to {time_str}\n\n"
                f"You will receive reminders at this time when the interval period has passed."
            )
            logger.info(f"Notification time set to {time_str} for chat {chat_id}")
        else:
            await update.message.reply_text("❌ Error setting notification time. Please try again.")
        
        return ConversationHandler.END
        
    except Exception as e:
        await update.message.reply_text("❌ Error processing time. Please try again.")
        logger.error(f"Error setting notification time for chat {chat_id}: {e}")
        return ConversationHandler.END


@execute_with_authentication()
async def cancel_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the time setting process."""
    await update.message.reply_text("❌ Notification time setting cancelled.")
    return ConversationHandler.END
