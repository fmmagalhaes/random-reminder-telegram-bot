#!/usr/bin/env python3
"""
Random Reminder Telegram Bot

This bot collects messages from a chat and randomly sends one back periodically
as a reminder of things previously shared.
"""

import os
import asyncio
from datetime import datetime, timedelta

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler
from dotenv import load_dotenv
from storage.message_storage import storage
from helpers.logger import setup_logger

# Import handlers
from handlers.command_handlers import start_command, stop_command, remind_command, list_command, delete_command, clear_command
from handlers.schedule_handlers import schedule_command, handle_cron_input, cancel_cron, WAITING_FOR_CRON
from handlers.message_handlers import handle_message
from helpers.reminder_utils import send_random_reminder
from helpers.time_utils import should_trigger_cron

load_dotenv()

# Setup logging
CURRENT_DIR = os.path.dirname(__file__)
logger = setup_logger(CURRENT_DIR)

# Global variables
application = None

async def check_and_send_reminders(context):
    """Check all active chats and send reminders based on cron expressions."""
    try:
        current_time = datetime.now()

        for chat_key in storage.data.keys():
            chat_id = int(chat_key)
            
            if not storage.get_chat_active_status(chat_id):
                continue

            # Get the cron expression for this chat
            cron_expression = storage.get_chat_cron_expression(chat_id)
            if not cron_expression:
                # No cron expression set, skip this chat
                continue

            last_datetime = storage.get_last_reminder_datetime(chat_id)
            
            # Check if the cron should trigger
            if should_trigger_cron(cron_expression, last_datetime):
                await send_random_reminder(chat_id, application=context.application)
                storage.set_last_reminder_datetime(chat_id, current_time)
                logger.info(f"Sent reminder to chat {chat_id} based on cron: {cron_expression}")

    except Exception as e:
        logger.error(f"Error in periodic reminders: {e}")


def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("BOT_TOKEN environment variable is not set! Please create a .env file with your Telegram bot token.")
        print("❌ BOT_TOKEN not found!")
        print("📝 Create a .env file with: BOT_TOKEN=your_bot_token_here")
        print("🤖 Get your token from @BotFather on Telegram")
        return
    
    application = ApplicationBuilder().token(token).build()

    # Create cron conversation handler
    cron_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("schedule", schedule_command)],
        states={
            WAITING_FOR_CRON: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_cron_input),
                CommandHandler("cancel", cancel_cron),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_cron)],
    )

    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", start_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CommandHandler("remind", remind_command))
    application.add_handler(CommandHandler("list", list_command))
    application.add_handler(CommandHandler("delete", delete_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(cron_conv_handler)
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    # Schedule periodic reminders
    application.job_queue.run_repeating(
        check_and_send_reminders,
        interval=60,
        first=30
    )
    
    logger.info("Bot started successfully!")
    application.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
