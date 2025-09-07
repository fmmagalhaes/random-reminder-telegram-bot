from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from storage.message_storage import storage
from helpers.logger import get_logger
from helpers.time_utils import format_interval_display
from helpers.auth_wrapper import execute_with_authentication

logger = get_logger()

# Conversation states
WAITING_FOR_INTERVAL = 1


@execute_with_authentication()
async def interval_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the interval setting process."""
    chat_id = update.effective_chat.id
    
    current_interval = storage.get_chat_interval(chat_id)
    
    time_str = format_interval_display(current_interval)
    
    await update.message.reply_text(
        f"⏰ Current reminder interval: {time_str}\n\n"
        f"Please send me the new interval in days.\n"
        f"Examples:\n"
        f"• 1 (1 day)\n"
        f"• 2 (2 days)\n"
        f"• 7 (1 week)\n\n"
        f"Send /cancel to cancel this operation."
    )
    
    return WAITING_FOR_INTERVAL


@execute_with_authentication()
async def handle_interval_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the interval input from the user."""
    chat_id = update.effective_chat.id
    
    try:
        new_interval = float(update.message.text)

        if new_interval < 1:
            await update.message.reply_text(
                "❌ Invalid interval! Minimum is 1 day.\n"
                "Please send a valid number or /cancel to cancel."
            )
            return WAITING_FOR_INTERVAL
        
        success = storage.set_chat_interval(chat_id, new_interval)
        
        if success:
            # Format the time for display
            time_str = format_interval_display(new_interval)
            
            await update.message.reply_text(
                f"✅ Reminder interval set to {time_str}!"
            )
            logger.info(f"Chat {chat_id} interval set to {new_interval} days")
        else:
            await update.message.reply_text(
                "❌ Failed to save interval setting. Please try again."
            )
        
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid number! Please send a valid number for days.\n"
            "Examples: 1 or 0.5\n\n"
            "Send /cancel to cancel this operation."
        )
        return WAITING_FOR_INTERVAL
    except Exception as e:
        await update.message.reply_text(
            "❌ Error setting interval. Please try again."
        )
        logger.error(f"Error setting interval for chat {chat_id}: {e}")
        return WAITING_FOR_INTERVAL


@execute_with_authentication()
async def cancel_interval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the interval setting process."""
    await update.message.reply_text("❌ Interval setting cancelled.")
    return ConversationHandler.END
