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
from handlers.interval_handlers import interval_command, handle_interval_input, cancel_interval, WAITING_FOR_INTERVAL
from handlers.time_handlers import time_command, handle_time_input, cancel_time, WAITING_FOR_TIME
from handlers.message_handlers import handle_message
from helpers.reminder_utils import send_random_reminder
from helpers.time_utils import is_notification_time

load_dotenv()

# Setup logging
CURRENT_DIR = os.path.dirname(__file__)
logger = setup_logger(CURRENT_DIR)

# Global variables
application = None

async def check_and_send_reminders(context):
    """Check all active chats and send reminders if enough time has passed."""
    try:
        current_time = datetime.now()

        for chat_key in storage.data.keys():
            chat_id = int(chat_key)
            
            if not storage.get_chat_active_status(chat_id):
                continue

            interval_days = storage.get_chat_interval(chat_id)
            last_datetime = storage.get_last_reminder_datetime(chat_id)
            notification_time = storage.get_chat_notification_time(chat_id)

            # If no last reminder time, try to send one now
            if last_datetime is None:
                # Check if it's already time to send based on notification time
                if notification_time and not is_notification_time(current_time, notification_time, last_datetime):
                    continue

                await send_random_reminder(chat_id, application=context.application)
                storage.set_last_reminder_datetime(chat_id, current_time)
                continue

            # Check if enough time has passed for this chat
            time_diff = current_time - last_datetime
            if time_diff >= timedelta(days=interval_days):
                # Check if it's already time to send based on notification time
                if notification_time and not is_notification_time(current_time, notification_time, last_datetime):
                    continue

                await send_random_reminder(chat_id, application=context.application)
                storage.set_last_reminder_datetime(chat_id, current_time)

    except Exception as e:
        logger.error(f"Error in periodic reminders: {e}")


def main():
    token = os.getenv("BOT_TOKEN")
    application = ApplicationBuilder().token(token).build()

    # Create interval conversation handler
    interval_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("interval", interval_command)],
        states={
            WAITING_FOR_INTERVAL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_interval_input),
                CommandHandler("cancel", cancel_interval),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_interval)],
    )

    # Create time conversation handler
    time_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("time", time_command)],
        states={
            WAITING_FOR_TIME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_time_input),
                CommandHandler("cancel", cancel_time),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_time)],
    )

    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", start_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CommandHandler("remind", remind_command))
    application.add_handler(CommandHandler("list", list_command))
    application.add_handler(CommandHandler("delete", delete_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(interval_conv_handler)
    application.add_handler(time_conv_handler)
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
