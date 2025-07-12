#!/usr/bin/env python3
"""
Setup script for List Bot
Helps users configure the bot easily
"""

import os
from pathlib import Path

def create_env_file():
    """Create .env file with template"""
    env_content = """# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Optional: Restrict bot to specific chat (get this from your group chat)
# AUTHORIZED_CHAT_ID=-1234567890
"""
    
    env_file = Path('.env')
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file")
    print("📝 Please edit .env file and add your bot token from @BotFather")

def main():
    """Main setup function"""
    print("🤖 List Bot Setup")
    print("=" * 30)
    
    # Create .env file
    create_env_file()
    
    print("\n🚀 Next steps:")
    print("1. Go to @BotFather on Telegram")
    print("2. Create a new bot")
    print("3. Copy the bot token")
    print("4. Edit .env file and replace 'your_bot_token_here' with your token")
    print("5. Run: python test_cli.py (to test locally)")
    print("6. Run: python telegram_bot.py (to start the bot)")
    
    print("\n🔧 Optional:")
    print("- Add AUTHORIZED_CHAT_ID to restrict bot to specific chat")
    print("- Check config.py to adjust limits and settings")

if __name__ == "__main__":
    main() 