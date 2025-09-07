from functools import wraps
from telegram import Update
from telegram.ext import CallbackContext
from helpers.logger import get_logger
import os

logger = get_logger()


def execute_with_authentication():
    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: CallbackContext):
            user_id = update.effective_user.id
            chat_id = update.effective_chat.id
            
            if not is_authorized_user(user_id):
                logger.warning(f"Unauthorized access attempt by user_id: {user_id}, chat_id: {chat_id}")
                return
            
            logger.info(f"Authorized access by user_id: {user_id}, chat_id: {chat_id}")
            return await func(update, context)
        
        return wrapper
    return decorator


def is_authorized_user(user_id: int) -> bool:
    env_user_ids = os.getenv('AUTHORIZED_USER_IDS')
    if env_user_ids:
        # Support multiple user IDs separated by commas
        try:
            authorized_user_ids = [int(user_id.strip()) for user_id in env_user_ids.split(',')]
            return user_id in authorized_user_ids
        except ValueError:
            logger.error(f"Invalid AUTHORIZED_USER_IDS format: {env_user_ids}. Should be comma-separated numbers.")
            return False
    return False
