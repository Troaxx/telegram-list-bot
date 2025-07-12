#!/usr/bin/env python3
"""
CLI Test Version of the List Bot
Run this to test the functionality before deploying to Telegram
"""

from typing import Tuple, Optional
import logging

from list_manager import ListManager
from config import Commands, Messages

# Set up logging for CLI
logging.basicConfig(level=logging.WARNING)


def parse_command(command: str) -> Tuple[Optional[str], list]:
    """Parse a command into action and arguments"""
    parts = command.strip().split()
    if not parts:
        return None, []
    
    action = parts[0].lower()
    args = parts[1:]
    
    return action, args


def display_welcome() -> None:
    """Display welcome message and instructions"""
    print("🤖 List Bot CLI Test")
    print("Type 'help' for commands or 'quit' to exit")
    print("-" * 40)
    print("\n💡 Quick start:")
    print("• create groceries")
    print("• add groceries milk")
    print("• multi groceries bread, eggs, butter")
    print("• show groceries")
    print("• lists")


def handle_command(list_manager: ListManager, action: str, args: list) -> None:
    """Handle a single command"""
    if action == Commands.HELP:
        print(list_manager.get_help())
    
    elif action == Commands.CREATE:
        if not args:
            print(Messages.USAGE_CREATE)
            return
        list_name = ' '.join(args)
        result = list_manager.create_list(list_name)
        print(result)
    
    elif action == Commands.LISTS:
        result = list_manager.show_all_lists()
        print(result)
    
    elif action == Commands.ADD:
        if len(args) < 2:
            print(Messages.USAGE_ADD)
            return
        list_name = args[0]
        item = ' '.join(args[1:])
        result = list_manager.add_item(list_name, item)
        print(result)
    
    elif action == Commands.REMOVE:
        if len(args) < 2:
            print(Messages.USAGE_REMOVE)
            return
        list_name = args[0]
        item = ' '.join(args[1:])
        result = list_manager.remove_item(list_name, item)
        print(result)
    
    elif action == Commands.SHOW:
        if not args:
            print(Messages.USAGE_SHOW)
            return
        list_name = ' '.join(args)
        result = list_manager.show_list(list_name)
        print(result)
    
    elif action == Commands.DELETE:
        if not args:
            print(Messages.USAGE_DELETE)
            return
        list_name = ' '.join(args)
        result = list_manager.delete_list(list_name)
        print(result)
    
    elif action == Commands.SEARCH:
        if not args:
            print(Messages.USAGE_SEARCH)
            return
        search_term = ' '.join(args)
        result = list_manager.search_item(search_term)
        print(result)
    
    elif action == 'stats':
        # Hidden command to show statistics
        stats = list_manager.get_stats()
        print("\n📊 **Statistics:**")
        print(f"• Total lists: {stats['total_lists']}")
        print(f"• Total items: {stats['total_items']}")
        if stats['total_lists'] > 0:
            print(f"• Average items per list: {stats['average_items_per_list']:.1f}")
            print(f"• Largest list size: {stats['largest_list_size']}")
    
    elif action == 'multi':
        # Simulate mention functionality: multi <list_name> <item1>, <item2>, <item3>
        if len(args) < 2:
            print("❌ Usage: multi <list_name> <item1>, <item2>, <item3>")
            return
        list_name = args[0]
        items_text = ' '.join(args[1:])
        result = list_manager.add_multiple_items(list_name, items_text)
        print(result)
    
    else:
        print(f"❌ Unknown command: {action}")
        print("Type 'help' for available commands")


def main():
    """Main CLI loop"""
    display_welcome()
    
    try:
        list_manager = ListManager()
    except Exception as e:
        print(f"❌ Error initializing list manager: {e}")
        return
    
    while True:
        try:
            command = input("\n> ").strip()
            
            if command.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not command:
                continue
                
            action, args = parse_command(command)
            
            if action:
                handle_command(list_manager, action, args)
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 