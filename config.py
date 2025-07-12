"""
Configuration constants and settings for the List Bot
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class BotConfig:
    """Bot configuration settings"""
    data_file: str = "lists_data.json"
    max_list_name_length: int = 50
    max_item_length: int = 200
    max_lists_per_user: int = 50
    max_items_per_list: int = 100
    backup_enabled: bool = True
    backup_interval_hours: int = 24


@dataclass
class TelegramConfig:
    """Telegram bot configuration"""
    token: Optional[str] = None
    authorized_chat_id: Optional[int] = None
    
    def __post_init__(self):
        if not self.token:
            self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        
        if not self.authorized_chat_id:
            chat_id = os.getenv('AUTHORIZED_CHAT_ID')
            if chat_id:
                try:
                    self.authorized_chat_id = int(chat_id)
                except ValueError:
                    pass


# Command constants
class Commands:
    """Available bot commands"""
    HELP = "help"
    CREATE = "create"
    LISTS = "lists"
    ADD = "add"
    REMOVE = "remove"
    SHOW = "show"
    DELETE = "delete"
    SEARCH = "search"
    
    ALL_COMMANDS = {
        HELP, CREATE, LISTS, ADD, REMOVE, SHOW, DELETE, SEARCH
    }


# Response messages
class Messages:
    """Response message templates"""
    LIST_CREATED = "✅ Created list '{name}'"
    LIST_EXISTS = "❌ List '{name}' already exists!"
    LIST_NOT_FOUND = "❌ List '{name}' not found!"
    ITEM_ADDED = "✅ Added '{item}' to '{list_name}'"
    ITEM_EXISTS = "⚠️ '{item}' is already in '{list_name}'"
    ITEM_REMOVED = "✅ Removed '{item}' from '{list_name}'"
    ITEM_NOT_FOUND = "❌ '{item}' not found in '{list_name}'"
    LIST_DELETED = "🗑️ Deleted list '{name}'"
    NO_LISTS = "📝 No lists created yet! Use 'create <list_name>' to create one."
    EMPTY_LIST = "📝 List '{name}' is empty"
    NO_SEARCH_RESULTS = "❌ No items found containing '{term}'"
    
    # Error messages
    INVALID_LIST_NAME = "❌ List name must be 1-{max_len} characters long"
    INVALID_ITEM = "❌ Item must be 1-{max_len} characters long"
    TOO_MANY_LISTS = "❌ Maximum {max_lists} lists allowed"
    TOO_MANY_ITEMS = "❌ Maximum {max_items} items per list allowed"
    
    # Usage messages
    USAGE_CREATE = "❌ Usage: `create <list_name>`"
    USAGE_ADD = "❌ Usage: `add <list_name> <item>`"
    USAGE_REMOVE = "❌ Usage: `remove <list_name> <item>`"
    USAGE_SHOW = "❌ Usage: `show <list_name>`"
    USAGE_DELETE = "❌ Usage: `delete <list_name>`"
    USAGE_SEARCH = "❌ Usage: `search <term>`" 