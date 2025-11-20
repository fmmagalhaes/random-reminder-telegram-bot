from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from storage.chat_repository import storage
from helpers.logger import get_logger
from helpers.auth_wrapper import execute_with_authentication
from pyslop.cronslator import cronslate

logger = get_logger()

# Conversation states
WAITING_FOR_CRON = 1


@execute_with_authentication()
async def schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the cron expression setting process."""
    chat_id = update.effective_chat.id
    
    current_cron = storage.get_chat_cron_expression(chat_id)
    current_cron_text = storage.get_chat_cron_text(chat_id)
    
    if current_cron and current_cron_text:
        cron_str = f"{current_cron_text} ({current_cron})"
    elif current_cron:
        cron_str = current_cron
    else:
        cron_str = "not set"
    
    await update.message.reply_text(
        f"⏰ Current schedule: {cron_str}\n\n"
        f"Please send me when you want to receive notifications in natural language.\n"
        f"Examples:\n"
        f"• Every monday at 3am\n"
        f"• Daily at 9:00 PM\n"
        f"• Every weekday at noon\n"
        f"• Every 2 hours\n\n"
        f"Send /cancel to cancel this operation."
    )
    
    return WAITING_FOR_CRON


@execute_with_authentication()
async def handle_cron_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the cron input from the user."""
    chat_id = update.effective_chat.id
    cron_text = update.message.text.strip()
    
    try:
        # Parse natural language to cron expression using cronslate function
        cron_expression = cronslate(cron_text)
        
        if not cron_expression:
            await update.message.reply_text(
                "❌ Could not parse the time expression! Please try a different format.\n"
                "Examples:\n"
                "• Every monday at 3am\n"
                "• Daily at 9:00 PM\n"
                "• Every weekday at noon\n\n"
                "Send /cancel to cancel this operation."
            )
            return WAITING_FOR_CRON
        
        success = storage.set_chat_cron(chat_id, cron_expression, cron_text)
        
        if success:
            await update.message.reply_text(
                f"✅ Schedule set!\n\n"
                f"📝 Natural language: {cron_text}\n"
                f"⚙️ Cron expression: {cron_expression}\n\n"
                f"Your reminders will be scheduled according to this schedule."
            )
            logger.info(f"Schedule expression set to '{cron_expression}' for chat {chat_id}")
        else:
            await update.message.reply_text("❌ Error saving schedule. Please try again.")
        
        return ConversationHandler.END
        
    except Exception as e:
        await update.message.reply_text(
            "❌ Error processing schedule. Please try again.\n"
            "Make sure to use clear natural language like:\n"
            "• Every monday at 3am\n"
            "• Daily at 9:00 PM"
        )
        logger.error(f"Error setting schedule expression for chat {chat_id}: {e}")
        return WAITING_FOR_CRON


@execute_with_authentication()
async def cancel_cron(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the cron setting process."""
    await update.message.reply_text("❌ Schedule setting cancelled.")
    return ConversationHandler.END