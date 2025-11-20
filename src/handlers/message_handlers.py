from telegram import Update
from telegram.ext import ContextTypes
from storage.chat_repository import storage
from helpers.logger import get_logger
from helpers.auth_wrapper import execute_with_authentication

logger = get_logger()


@execute_with_authentication()
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages and store them."""
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    
    result = storage.store_message(chat_id, update.message)
    if result:
        await update.message.reply_text("✅ Message stored successfully!")
    else:
        await update.message.reply_text("❌ Failed to store message.")
