# 🤖 Telegram List Bot

A Telegram bot that manages lists using simple keyword commands. Perfect for private group chats!

## 🎯 Features

- **Create & manage multiple lists** with simple commands
- **Add/remove items** from lists
- **Quick add multiple items** by mentioning the bot: `@bot groceries milk, bread, eggs`
- **Search across all lists** for specific items
- **Case-insensitive commands** for easy use
- **Data persistence** - your lists are saved between bot restarts
- **Group chat friendly** - works in private group chats
- **No slash commands required** - just type naturally!

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Test in Terminal First

```bash
python test_cli.py
```

### 3. Set up Telegram Bot

1. Create a bot with [@BotFather](https://t.me/BotFather) on Telegram
2. Create a `.env` file with your bot token:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

3. (Optional) Restrict to specific chat:
```
AUTHORIZED_CHAT_ID=-1234567890
```

### 4. Run the Bot

```bash
python telegram_bot.py
```

## 📋 Example Usage & Output

Here's what the bot output looks like:

### Creating Lists
```
> create groceries
✅ Created list 'groceries'

> create movies to watch
✅ Created list 'movies to watch'
```

### Adding Items
```
> add groceries milk
✅ Added 'milk' to 'groceries'

> add groceries bread
✅ Added 'bread' to 'groceries'

> add groceries eggs
✅ Added 'eggs' to 'groceries'

> add movies Django Unchained
✅ Added 'Django Unchained' to 'movies to watch'
```

### Quick Add with Mentions (Multiple Items)
```
> @bot groceries butter, cheese, yogurt
✅ Added 3 items to 'groceries':
  • butter
  • cheese  
  • yogurt

> @bot movies The Godfather, Pulp Fiction, Goodfellas
✅ Added 3 items to 'movies to watch':
  • The Godfather
  • Pulp Fiction
  • Goodfellas
```

### Viewing Lists
```
> show groceries
📋 **groceries** (3 items):
1. milk
2. bread
3. eggs

> lists
📚 **All Lists:**
• groceries (3 items)
• movies to watch (1 items)
```

### Searching
```
> search milk
🔍 **Search results for 'milk':**
📋 groceries: milk

> search django
🔍 **Search results for 'django':**
📋 movies to watch: Django Unchained
```

### Removing Items
```
> remove groceries milk
✅ Removed 'milk' from 'groceries'

> show groceries
📋 **groceries** (2 items):
1. bread
2. eggs
```

## 🎮 Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `create <list_name>` | Create a new list | `create groceries` |
| `lists` | Show all lists | `lists` |
| `add <list_name> <item>` | Add item to list | `add groceries milk` |
| `@bot <list_name> <item1>, <item2>` | Add multiple items at once | `@meowlister_bot groceries milk, bread, eggs` |
| `remove <list_name> <item>` | Remove item from list | `remove groceries milk` |
| `show <list_name>` | Show all items in list | `show groceries` |
| `delete <list_name>` | Delete entire list | `delete groceries` |
| `search <term>` | Search for items | `search milk` |
| `help` | Show help message | `help` |

## 🔧 Features

- **Case-insensitive**: `GROCERIES`, `groceries`, and `Groceries` all work
- **Multi-word support**: List names and items can have spaces
- **Persistent storage**: Data saved in `lists_data.json`
- **Error handling**: Helpful error messages for invalid commands
- **Group chat ready**: Works in private group chats
- **No duplicates**: Won't add the same item twice to a list

## 🛠️ Files Structure

- `telegram_bot.py` - Main Telegram bot
- `list_manager.py` - Core list management logic
- `test_cli.py` - CLI version for testing
- `requirements.txt` - Python dependencies
- `lists_data.json` - Data storage (created automatically)

## 📱 Telegram Setup

1. **Create a bot**: Message [@BotFather](https://t.me/BotFather)
2. **Get your token**: Copy the token from BotFather
3. **Add to group**: Add your bot to your private group
4. **Get chat ID** (optional): For restricting bot to specific chat

## 🧪 Testing

Test the functionality locally first:

```bash
python test_cli.py
```

This lets you test all commands before deploying to Telegram!

## 🔒 Security

- Bot can be restricted to specific chat IDs
- No external API calls (data stays local)
- Simple file-based storage
- No sensitive data handling

## 🚀 Deployment

For production deployment, consider:
- Using a database instead of JSON files
- Adding user authentication
- Implementing backup strategies
- Using a process manager like PM2

---

**Happy list managing! 🎉** 
