from telegram import Update
from telegram.ext import ContextTypes
from storage.chat_repository import storage
from helpers.logger import get_logger
from helpers.reminder_utils import send_random_reminder
from helpers.auth_wrapper import execute_with_authentication

logger = get_logger()


@execute_with_authentication()
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command"""
    chat_id = update.effective_chat.id
    
    storage.set_chat_active_status(chat_id, True)

    welcome_message = (
        "🤖 Random Reminder Bot started!\n\n"
        "I'll collect messages from this chat and randomly remind you "
        "of them every day. Send me some messages to get started!\n\n"
        "⚠️ Make this bot an admin in your group/channel "
        "so it can collect your messages.\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/stop - Stop random reminders\n"
        "/remind - Get a random message now\n"
        "/schedule - Set reminder schedule\n"
        "/list - Show all stored messages\n"
        "/delete <number> - Delete a specific message\n"
        "/clear - Delete all stored messages"
    )

    await update.message.reply_text(welcome_message)
    logger.info(f"Bot started in chat {chat_id}")


@execute_with_authentication()
async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /stop command"""
    chat_id = update.effective_chat.id
    
    storage.set_chat_active_status(chat_id, False)

    await update.message.reply_text(
        "🛑 Random reminders stopped for this chat. "
        "Use /start to resume."
    )
    logger.info(f"Bot stopped in chat {chat_id}")


@execute_with_authentication()
async def remind_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /remind command"""
    chat_id = update.effective_chat.id
    await send_random_reminder(chat_id, context.application)


@execute_with_authentication()
async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /list command - show all stored messages with numbers"""
    chat_id = update.effective_chat.id
    
    messages = storage.get_all_messages(chat_id)
    
    if not messages:
        await update.message.reply_text(
            "📝 No messages stored yet!\n\n"
            "Send me some messages first, and I'll collect them for random reminders."
        )
        return
    
    message_list = "📝 **Stored Messages:**\n\n"
    for i, message in enumerate(messages, 1):
        # Truncate long messages for display
        display_message = message[:200] + "..." if len(message) > 200 else message
        message_list += f"{i} - {display_message}\n\n"
    
    message_list += "🗑️ Use /delete <number> to delete a specific message"
    
    await update.message.reply_text(message_list, parse_mode='Markdown')
    logger.info(f"Listed {len(messages)} messages for chat {chat_id}")


@execute_with_authentication()
async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /delete command - delete a message by number"""
    chat_id = update.effective_chat.id
    
    try:
        message_number = int(context.args[0])
        message_index = message_number - 1 # Convert to 0-based index
        
        # Get current messages to show what we're deleting
        messages = storage.get_all_messages(chat_id)
        
        if message_index >= len(messages):
            await update.message.reply_text(
                f"❌ Message number {message_number} doesn't exist.\n\n"
                "Use /list to see all messages with their numbers."
            )
            return
        
        # Show what we're deleting
        message_to_delete = messages[message_index]
        display_message = message_to_delete[:500] + "..." if len(message_to_delete) > 500 else message_to_delete
        
        # Delete the message
        success = storage.delete_message_by_index(chat_id, message_index)
        
        if success:
            await update.message.reply_text(f"Deleted: _{display_message}_\n\n", parse_mode='Markdown')
            logger.info(f"Deleted message {message_number} from chat {chat_id}")
        else:
            await update.message.reply_text("❌ Failed to delete message.")

    except (ValueError, IndexError):
        await update.message.reply_text(
            "❌ Invalid message number! Please provide a valid number.\n\n"
            "Example: /delete 3\n\n"
            "Use /list to see all messages with their numbers."
        )
    except Exception as e:
        await update.message.reply_text("❌ Error deleting message.")
        logger.error(f"Error deleting message for chat {chat_id}: {e}")


@execute_with_authentication()
async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /clear command - delete all stored messages with confirmation"""
    chat_id = update.effective_chat.id
    
    # Get current message count
    message_count = storage.get_message_count(chat_id)
    
    if message_count == 0:
        await update.message.reply_text("📝 No messages stored to clear!")
        return
    
    # Check if user provided confirmation
    if context.args and context.args[0].lower() == 'confirm':
        # User confirmed, proceed with clearing
        success = storage.clear_all_messages(chat_id)
        
        if success:
            await update.message.reply_text(
                f"🗑️ {message_count} message{'s' if message_count != 1 else ''} deleted!\n\n"
                f"💡 Send me new messages to start collecting again.",
                parse_mode='Markdown'
            )
            logger.info(f"Cleared all {message_count} messages from chat {chat_id}")
        else:
            await update.message.reply_text("❌ Failed to clear messages.")
    else:
        # Show confirmation prompt
        await update.message.reply_text(
            f"⚠️ **Are you sure you want to delete ALL messages?**\n\n"
            f"This will permanently delete all {message_count} stored message{'s' if message_count != 1 else ''}.\n\n"
            f"To confirm, use: /clear confirm\n"
            f"To cancel, just ignore this message.",
            parse_mode='Markdown'
        )
