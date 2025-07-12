#!/usr/bin/env python3
"""
Telegram List Bot
A bot that manages lists with keyword commands for private group chats
"""

import logging
from typing import Optional
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from dotenv import load_dotenv

from list_manager import ListManager
from config import BotConfig, TelegramConfig, Commands, Messages

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramListBot:
    """
    Telegram bot that manages lists with keyword commands.
    
    Handles user interactions and delegates list operations to ListManager.
    """
    
    def __init__(self, telegram_config: TelegramConfig, bot_config: Optional[BotConfig] = None) -> None:
        """
        Initialize the Telegram bot.
        
        Args:
            telegram_config: Telegram-specific configuration
            bot_config: General bot configuration
        """
        self.telegram_config = telegram_config
        self.bot_config = bot_config or BotConfig()
        self.list_manager = ListManager(self.bot_config)
        
        logger.info("Telegram List Bot initialized")
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Start command handler"""
        welcome_message = """🤖 **List Bot is ready!**

I'll help you manage lists in this group chat using simple keyword commands.

Type any of these commands to get started:
• `help` - Show all available commands
• `create groceries` - Create a new list
• `lists` - Show all your lists

I work with natural language - just type the commands without slashes!

**Quick Example:**
• `create shopping`
• `add shopping milk`
• `add shopping bread`
• `show shopping`"""
        
        await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)
        logger.info(f"Start command from user {update.effective_user.id} in chat {update.message.chat_id}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Help command handler"""
        help_text = self.list_manager.get_help()
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
        logger.info(f"Help command from user {update.effective_user.id} in chat {update.message.chat_id}")
    
    def _is_authorized_chat(self, chat_id: int) -> bool:
        """Check if the chat is authorized to use the bot"""
        if not self.telegram_config.authorized_chat_id:
            return True  # No restriction
        return chat_id == self.telegram_config.authorized_chat_id
    
    def _parse_command(self, message_text: str) -> tuple:
        """Parse a message into command and arguments"""
        parts = message_text.strip().split()
        if not parts:
            return None, []
        
        command = parts[0].lower()
        args = parts[1:]
        
        return command, args
    
    async def _handle_command(self, command: str, args: list) -> Optional[str]:
        """Handle a specific command and return the response"""
        if command == Commands.HELP:
            return self.list_manager.get_help()
        
        elif command == Commands.CREATE:
            if not args:
                return Messages.USAGE_CREATE
            list_name = ' '.join(args)
            return self.list_manager.create_list(list_name)
        
        elif command == Commands.LISTS:
            return self.list_manager.show_all_lists()
        
        elif command == Commands.ADD:
            if len(args) < 2:
                return Messages.USAGE_ADD
            list_name = args[0]
            item = ' '.join(args[1:])
            return self.list_manager.add_item(list_name, item)
        
        elif command == Commands.REMOVE:
            if len(args) < 2:
                return Messages.USAGE_REMOVE
            list_name = args[0]
            item = ' '.join(args[1:])
            return self.list_manager.remove_item(list_name, item)
        
        elif command == Commands.SHOW:
            if not args:
                return Messages.USAGE_SHOW
            list_name = ' '.join(args)
            return self.list_manager.show_list(list_name)
        
        elif command == Commands.DELETE:
            if not args:
                return Messages.USAGE_DELETE
            list_name = ' '.join(args)
            return self.list_manager.delete_list(list_name)
        
        elif command == Commands.SEARCH:
            if not args:
                return Messages.USAGE_SEARCH
            search_term = ' '.join(args)
            return self.list_manager.search_item(search_term)
        
        elif command == 'stats':
            # Hidden command for debugging
            stats = self.list_manager.get_stats()
            return f"""📊 **Bot Statistics:**
• Total lists: {stats['total_lists']}
• Total items: {stats['total_items']}
• Average items per list: {stats['average_items_per_list']:.1f}
• Largest list size: {stats['largest_list_size']}"""
        
        return None  # Unknown command
    
    def _parse_mention(self, message_text: str, bot_username: str) -> tuple:
        """
        Parse a mention to extract list name and items.
        
        Expected format: @bot_username <list_name> <item1>, <item2>, <item3>
        
        Returns:
            tuple: (list_name, items_text) or (None, None) if invalid
        """
        # Remove the @bot_username from the beginning
        mention_prefix = f"@{bot_username}"
        if not message_text.startswith(mention_prefix):
            return None, None
        
        # Get the text after the mention
        remaining_text = message_text[len(mention_prefix):].strip()
        
        if not remaining_text:
            return None, None
        
        # Split into list name and items
        parts = remaining_text.split(None, 1)  # Split on first whitespace
        if len(parts) < 2:
            return None, None
        
        list_name = parts[0]
        items_text = parts[1]
        
        return list_name, items_text
    
    async def handle_mention(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle when the bot is mentioned for quick item adding"""
        message_text = update.message.text.strip()
        
        # Get bot username
        bot_username = context.bot.username
        
        # Parse the mention
        list_name, items_text = self._parse_mention(message_text, bot_username)
        
        if not list_name or not items_text:
            # Invalid mention format
            help_text = f"""❌ Invalid mention format!

**Quick Add Usage:**
`@{bot_username} <list_name> <item1>, <item2>, <item3>`

**Example:**
`@{bot_username} groceries milk, bread, eggs`"""
            
            await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
            return
        
        try:
            # Use the new add_multiple_items method
            response = self.list_manager.add_multiple_items(list_name, items_text)
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            
            logger.info(f"Processed mention from user {update.effective_user.id} in chat {update.message.chat_id}: {list_name} <- {items_text}")
            
        except Exception as e:
            logger.error(f"Error processing mention '{message_text}': {e}")
            await update.message.reply_text("❌ An error occurred while processing your mention.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle all text messages - both mentions and regular commands"""
        # Check authorization
        if not self._is_authorized_chat(update.message.chat_id):
            logger.warning(f"Unauthorized chat {update.message.chat_id} tried to use bot")
            return
        
        # Log chat ID for easy identification
        logger.info(f"📋 CHAT ID: {update.message.chat_id} (User: {update.effective_user.id})")
        
        message_text = update.message.text.strip()
        
        # Ignore empty messages
        if not message_text:
            return
        
        # Check if this is a mention
        if update.message.entities and any(entity.type == "mention" for entity in update.message.entities):
            await self.handle_mention(update, context)
            return
        
        # Parse the command
        command, args = self._parse_command(message_text)
        
        if not command:
            return
        
        try:
            response = await self._handle_command(command, args)
            
            if response:
                await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
                logger.info(f"Processed command '{command}' from user {update.effective_user.id} in chat {update.message.chat_id}")
            else:
                # Unknown command - don't respond to avoid spam
                logger.debug(f"Unknown command '{command}' from user {update.effective_user.id} in chat {update.message.chat_id}")
                
        except Exception as e:
            logger.error(f"Error processing message '{message_text}': {e}")
            await update.message.reply_text("❌ An error occurred while processing your request.")


def create_application(telegram_config: TelegramConfig, bot_config: Optional[BotConfig] = None) -> Application:
    """Create and configure the Telegram application"""
    bot = TelegramListBot(telegram_config, bot_config)
    
    application = Application.builder().token(telegram_config.token).build()
    
    # Add handlers in order of priority
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("help", bot.help_command))
    
    # Handle ALL text messages (simplified - no filters except commands)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        bot.handle_message
    ))
    
    return application


def main():
    """Main function to run the bot"""
    # Load configuration
    telegram_config = TelegramConfig()
    bot_config = BotConfig()
    
    # Validate configuration
    if not telegram_config.token:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in environment variables!")
        print("Please create a .env file with your bot token:")
        print("TELEGRAM_BOT_TOKEN=your_bot_token_here")
        print("\nOptional: Add AUTHORIZED_CHAT_ID to restrict bot to specific chat")
        return
    
    try:
        # Create and run application
        application = create_application(telegram_config, bot_config)
        
        # Start the bot
        print("🤖 Starting List Bot...")
        if telegram_config.authorized_chat_id:
            print(f"🔒 Restricted to chat ID: {telegram_config.authorized_chat_id}")
        else:
            print("🌐 Open to all chats")
        print("Press Ctrl+C to stop the bot")
        
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        print(f"❌ Error starting bot: {e}")


if __name__ == "__main__":
    main() 