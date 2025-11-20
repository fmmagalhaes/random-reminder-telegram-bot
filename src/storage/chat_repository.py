import os
import random
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from telegram import Message
from helpers.logger import get_logger

logger = get_logger()

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class ChatRepository:
    def __init__(self, json_file_path: str):
        self.json_file = json_file_path
        self.data = self._load_data()

    def _load_data(self) -> Dict:
        try:
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading data from JSON: {e}")
            return {}

    def _save_data(self):
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving data to JSON: {e}")

    def _ensure_chat_data(self, chat_id: int):
        """Ensure chat data exists with default values."""
        chat_key = str(chat_id)
        if chat_key not in self.data:
            self.data[chat_key] = {
                "messages": [],
                "active": True,
                "last_reminder_datetime": None,
                "cron_expression": None,
                "cron_text": None
            }

    def store_message(self, chat_id: int, message: Message):
        try:
            chat_key = str(chat_id)

            self._ensure_chat_data(chat_id)

            if message.text in self.data[chat_key]["messages"]:
                return True  # Message already exists

            self.data[chat_key]["messages"].append(message.text)
            self._save_data()

            logger.info(f"Stored message from chat {chat_id}: {message.text[:50]}...")

            return True

        except Exception as e:
            logger.error(f"Error storing message: {e}")
            return False

    def get_random_message(self, chat_id: int) -> Optional[str]:
        try:
            chat_key = str(chat_id)

            if chat_key not in self.data:
                return None

            messages = self.data[chat_key].get("messages", [])

            if not messages:
                return None

            return random.choice(messages)

        except Exception as e:
            logger.error(f"Error getting random message: {e}")
            return None

    def get_chat_active_status(self, chat_id: int) -> bool:
        try:
            chat_key = str(chat_id)

            if chat_key not in self.data:
                return False  # Default to inactive

            return self.data[chat_key].get("active", False)

        except Exception as e:
            logger.error(f"Error getting chat active status: {e}")
            return False

    def set_chat_active_status(self, chat_id: int, active: bool) -> bool:
        try:
            chat_key = str(chat_id)

            self._ensure_chat_data(chat_id)
            self.data[chat_key]["active"] = active
            self._save_data()

            logger.info(f"Set active status for chat {chat_id} to {active}")
            return True

        except Exception as e:
            logger.error(f"Error setting chat active status: {e}")
            return False

    def get_last_reminder_datetime(self, chat_id: int) -> Optional[datetime]:
        try:
            chat_key = str(chat_id)

            datetime_str = self.data[chat_key].get("last_reminder_datetime", None)
            if not datetime_str:
                return None

            return datetime.strptime(datetime_str, DATETIME_FORMAT)

        except Exception as e:
            logger.error(f"Error getting last reminder datetime: {e}")
            return None

    def set_last_reminder_datetime(self, chat_id: int, dt: datetime) -> bool:
        try:
            chat_key = str(chat_id)

            # Convert datetime to readable datetime string
            readable_datetime = dt.strftime(DATETIME_FORMAT)
            self.data[chat_key]["last_reminder_datetime"] = readable_datetime
            self._save_data()

            logger.info(f"Set last reminder datetime for chat {chat_id} to {readable_datetime}")
            return True

        except Exception as e:
            logger.error(f"Error setting last reminder datetime: {e}")
            return False

    def get_all_messages(self, chat_id: int) -> list:
        try:
            chat_key = str(chat_id)
            
            if chat_key not in self.data:
                return []
            
            return self.data[chat_key].get("messages", [])
            
        except Exception as e:
            logger.error(f"Error getting all messages: {e}")
            return []

    def delete_message_by_index(self, chat_id: int, index: int) -> bool:
        """Delete a message by its index (0-based)."""
        try:
            chat_key = str(chat_id)
            
            if chat_key not in self.data:
                return False
            
            messages = self.data[chat_key].get("messages", [])
            
            if index < 0 or index >= len(messages):
                return False
            
            deleted_message = messages.pop(index)
            self._save_data()
            
            logger.info(f"Deleted message {index + 1} from chat {chat_id}: {deleted_message[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting message by index: {e}")
            return False

    def get_message_count(self, chat_id: int) -> int:
        try:
            chat_key = str(chat_id)
            
            if chat_key not in self.data:
                return 0
            
            return len(self.data[chat_key].get("messages", []))
            
        except Exception as e:
            logger.error(f"Error getting message count: {e}")
            return 0

    def clear_all_messages(self, chat_id: int) -> bool:
        try:
            chat_key = str(chat_id)
            
            if chat_key not in self.data:
                return True  # Already no messages
            
            message_count = len(self.data[chat_key].get("messages", []))
            self.data[chat_key]["messages"] = []
            self._save_data()
            
            logger.info(f"Cleared {message_count} messages from chat {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing all messages: {e}")
            return False

    def get_chat_cron_expression(self, chat_id: int) -> Optional[str]:
        try:
            chat_key = str(chat_id)
            if chat_key in self.data:
                return self.data[chat_key].get("cron_expression")
            return None
        except Exception as e:
            logger.error(f"Error getting cron expression: {e}")
            return None

    def set_chat_cron_expression(self, chat_id: int, cron_expression: str) -> bool:
        try:
            chat_key = str(chat_id)

            self._ensure_chat_data(chat_id)
            self.data[chat_key]["cron_expression"] = cron_expression
            self._save_data()

            logger.info(f"Set cron expression for chat {chat_id} to {cron_expression}")
            return True

        except Exception as e:
            logger.error(f"Error setting cron expression: {e}")
            return False

    def get_chat_cron_text(self, chat_id: int) -> Optional[str]:
        try:
            chat_key = str(chat_id)
            if chat_key in self.data:
                return self.data[chat_key].get("cron_text")
            return None
        except Exception as e:
            logger.error(f"Error getting cron text: {e}")
            return None

    def set_chat_cron(self, chat_id: int, cron_expression: str, cron_text: str) -> bool:
        try:
            chat_key = str(chat_id)

            self._ensure_chat_data(chat_id)
            self.data[chat_key]["cron_expression"] = cron_expression
            self.data[chat_key]["cron_text"] = cron_text
            self._save_data()

            logger.info(f"Set cron for chat {chat_id}: '{cron_text}' -> {cron_expression}")
            return True

        except Exception as e:
            logger.error(f"Error setting cron: {e}")
            return False


def get_messages_file_path():
    """Get the messages file path from environment or default location."""
    env_path = os.getenv('MESSAGES_FILE')
    if env_path:
        return env_path
    
    # Go up from src/storage/ to project root, then to data/
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "data"
    
    os.makedirs(data_dir, exist_ok=True)
    
    return str(data_dir / "messages.json")

MESSAGES_FILE = get_messages_file_path()
storage = ChatRepository(MESSAGES_FILE)