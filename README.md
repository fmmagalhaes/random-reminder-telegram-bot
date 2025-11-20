# Random Reminder Telegram Bot
A Telegram bot that collects messages from a chat and randomly sends one back periodically as a reminder of things previously shared.

Inspired by Readwise, which sends reminders of personal highlights from books and articles.

## Setup

### 1. Create a Telegram Bot

1. Message @BotFather on Telegram
2. Send `/newbot` and follow the instructions
3. Choose a name and username for your bot
4. Save the bot token you receive

### 2. Install Dependencies

```bash
# Create and activate virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 3. Configure the Bot

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your bot token and authorized user ID:
   ```
   BOT_TOKEN=your_token
   AUTHORIZED_USER_IDS=your_user_id_here
   ```

3. Find your user ID:
   - You can find your user ID by messaging @userinfobot on Telegram
   - Or start the bot and check the logs when you send a message
   - For multiple users, separate IDs with commas: `123456789,987654321`

### 4. Run the Bot

```bash
python bot.py
```

## Usage

### Bot Commands

- `/start` - Start the bot and enable random reminders
- `/stop` - Stop random reminders for this chat
- `/remind` - Get a random message immediately
- `/schedule` - Set reminder schedule
- `/list` - Show all stored messages
- `/delete <number>` - Delete a specific message
- `/clear` - Delete all stored messages

### How it Works

1. Add the bot to your chat or group
2. Send `/start` to activate the bot
3. Start chatting! The bot will collect all text messages
4. Use `/schedule` to customize when reminders are sent using natural language:
   - "Every monday at 3am"
   - "Daily at 9:00 PM"
   - "Every weekday at noon"
   - "Every 2 hours"

## Storage

The bot uses a simple JSON file to store messages and chat configs locally in `messages.json`.