"""
List Manager - Core functionality for managing multiple lists
"""

import json
import logging
import os
import shutil
from datetime import datetime
import pytz
from typing import Dict, List, Optional

from config import BotConfig, Messages
from exceptions import (
    DataStorageError,
    ItemExistsError,
    ItemNotFoundError,
    LimitExceededError,
    ListExistsError,
    ListNotFoundError,
    ValidationError
)

logger = logging.getLogger(__name__)


class ListManager:
    """
    Manages multiple lists with persistent storage and validation.
    
    Supports operations like creating lists, adding/removing items,
    searching across lists, and data persistence.
    """
    
    def __init__(self, config: Optional[BotConfig] = None) -> None:
        """
        Initialize the ListManager.
        
        Args:
            config: Configuration object. If None, uses default config.
        """
        self.config = config or BotConfig()
        self.data_file = self.config.data_file
        self.lists: Dict[str, List[str]] = {}
        self._load_data()
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _load_data(self) -> None:
        """Load lists from JSON file with error handling."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Validate loaded data
                    if isinstance(data, dict):
                        self.lists = data
                    else:
                        logger.warning(f"Invalid data format in {self.data_file}")
                        self.lists = {}
            else:
                self.lists = {}
                logger.info(f"Data file {self.data_file} not found, starting fresh")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading data: {e}")
            self._backup_corrupted_file()
            self.lists = {}
    
    def _backup_corrupted_file(self) -> None:
        """Create a backup of corrupted data file."""
        if os.path.exists(self.data_file):
            backup_name = f"{self.data_file}.backup_{datetime.now(pytz.UTC).strftime('%Y%m%d_%H%M%S')}"
            try:
                shutil.copy2(self.data_file, backup_name)
                logger.info(f"Corrupted file backed up to {backup_name}")
            except IOError as e:
                logger.error(f"Failed to backup corrupted file: {e}")
    
    def _save_data(self) -> None:
        """Save lists to JSON file with error handling."""
        try:
            # Create backup if enabled
            if self.config.backup_enabled and os.path.exists(self.data_file):
                backup_name = f"{self.data_file}.backup"
                shutil.copy2(self.data_file, backup_name)
            
            # Save data
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.lists, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"Data saved to {self.data_file}")
        except IOError as e:
            logger.error(f"Error saving data: {e}")
            raise DataStorageError(f"Failed to save data: {e}")
    
    def _validate_list_name(self, list_name: str) -> None:
        """Validate list name format and length."""
        if not list_name or not list_name.strip():
            raise ValidationError("List name cannot be empty")
        
        list_name = list_name.strip()
        if len(list_name) > self.config.max_list_name_length:
            raise ValidationError(
                Messages.INVALID_LIST_NAME.format(max_len=self.config.max_list_name_length)
            )
    
    def _validate_item(self, item: str) -> None:
        """Validate item format and length."""
        if not item or not item.strip():
            raise ValidationError("Item cannot be empty")
        
        item = item.strip()
        if len(item) > self.config.max_item_length:
            raise ValidationError(
                Messages.INVALID_ITEM.format(max_len=self.config.max_item_length)
            )
    
    def _find_list_name(self, list_name: str) -> Optional[str]:
        """Find the actual list name (case-insensitive)."""
        list_name_lower = list_name.lower()
        for name in self.lists.keys():
            if name.lower() == list_name_lower:
                return name
        return None
    
    def _check_list_limit(self) -> None:
        """Check if creating a new list would exceed the limit."""
        if len(self.lists) >= self.config.max_lists_per_user:
            raise LimitExceededError(
                Messages.TOO_MANY_LISTS.format(max_lists=self.config.max_lists_per_user)
            )
    
    def _check_item_limit(self, list_name: str) -> None:
        """Check if adding an item would exceed the limit."""
        if len(self.lists[list_name]) >= self.config.max_items_per_list:
            raise LimitExceededError(
                Messages.TOO_MANY_ITEMS.format(max_items=self.config.max_items_per_list)
            )
    
    def create_list(self, list_name: str) -> str:
        """
        Create a new list.
        
        Args:
            list_name: Name of the list to create
            
        Returns:
            Success or error message
            
        Raises:
            ValidationError: If list name is invalid
            ListExistsError: If list already exists
            LimitExceededError: If too many lists
        """
        try:
            self._validate_list_name(list_name)
            self._check_list_limit()
            
            list_name = list_name.strip()
            
            if self._find_list_name(list_name):
                raise ListExistsError(Messages.LIST_EXISTS.format(name=list_name))
            
            self.lists[list_name] = []
            self._save_data()
            
            logger.info(f"Created list: {list_name}")
            return Messages.LIST_CREATED.format(name=list_name)
            
        except (ValidationError, ListExistsError, LimitExceededError) as e:
            logger.warning(f"Failed to create list '{list_name}': {e}")
            return str(e)
        except Exception as e:
            logger.error(f"Unexpected error creating list '{list_name}': {e}")
            return f"❌ An error occurred while creating the list"
    
    def add_item(self, list_name: str, item: str) -> str:
        """
        Add item to a list.
        
        Args:
            list_name: Name of the list
            item: Item to add
            
        Returns:
            Success or error message
        """
        try:
            self._validate_item(item)
            
            actual_list_name = self._find_list_name(list_name)
            if not actual_list_name:
                raise ListNotFoundError(Messages.LIST_NOT_FOUND.format(name=list_name))
            
            self._check_item_limit(actual_list_name)
            
            item = item.strip()
            
            if item in self.lists[actual_list_name]:
                raise ItemExistsError(Messages.ITEM_EXISTS.format(item=item, list_name=actual_list_name))
            
            self.lists[actual_list_name].append(item)
            self._save_data()
            
            logger.info(f"Added '{item}' to '{actual_list_name}'")
            return Messages.ITEM_ADDED.format(item=item, list_name=actual_list_name)
            
        except (ValidationError, ListNotFoundError, ItemExistsError, LimitExceededError) as e:
            logger.warning(f"Failed to add item '{item}' to '{list_name}': {e}")
            return str(e)
        except Exception as e:
            logger.error(f"Unexpected error adding item '{item}' to '{list_name}': {e}")
            return f"❌ An error occurred while adding the item"
    
    def add_multiple_items(self, list_name: str, items_text: str) -> str:
        """
        Add multiple items to a list, separated by commas.
        
        Args:
            list_name: Name of the list
            items_text: Comma-separated items to add
            
        Returns:
            Success or error message with summary
        """
        try:
            actual_list_name = self._find_list_name(list_name)
            if not actual_list_name:
                raise ListNotFoundError(Messages.LIST_NOT_FOUND.format(name=list_name))
            
            # Split by comma and clean up items
            items = [item.strip() for item in items_text.split(',') if item.strip()]
            
            if not items:
                raise ValidationError("No valid items found")
            
            # Check if we'd exceed the limit
            if len(self.lists[actual_list_name]) + len(items) > self.config.max_items_per_list:
                raise LimitExceededError(
                    f"❌ Adding {len(items)} items would exceed the limit of {self.config.max_items_per_list} items per list"
                )
            
            added_items = []
            skipped_items = []
            failed_items = []
            
            for item in items:
                try:
                    self._validate_item(item)
                    
                    if item in self.lists[actual_list_name]:
                        skipped_items.append(item)
                    else:
                        self.lists[actual_list_name].append(item)
                        added_items.append(item)
                        
                except ValidationError as e:
                    failed_items.append(f"{item} (invalid)")
                except Exception as e:
                    failed_items.append(f"{item} (error)")
            
            # Save data if we added anything
            if added_items:
                self._save_data()
                logger.info(f"Added {len(added_items)} items to '{actual_list_name}': {added_items}")
            
            # Build response message
            result_parts = []
            
            if added_items:
                result_parts.append(f"✅ Added {len(added_items)} items to '{actual_list_name}':")
                for item in added_items:
                    result_parts.append(f"  • {item}")
            
            if skipped_items:
                result_parts.append(f"⚠️ Skipped {len(skipped_items)} duplicate items:")
                for item in skipped_items:
                    result_parts.append(f"  • {item}")
            
            if failed_items:
                result_parts.append(f"❌ Failed to add {len(failed_items)} items:")
                for item in failed_items:
                    result_parts.append(f"  • {item}")
            
            if not result_parts:
                return "❌ No items were processed"
            
            return "\n".join(result_parts)
            
        except (ValidationError, ListNotFoundError, LimitExceededError) as e:
            logger.warning(f"Failed to add multiple items to '{list_name}': {e}")
            return str(e)
        except Exception as e:
            logger.error(f"Unexpected error adding multiple items to '{list_name}': {e}")
            return f"❌ An error occurred while adding the items"
    
    def remove_item(self, list_name: str, item: str) -> str:
        """
        Remove item from a list.
        
        Args:
            list_name: Name of the list
            item: Item to remove
            
        Returns:
            Success or error message
        """
        try:
            actual_list_name = self._find_list_name(list_name)
            if not actual_list_name:
                raise ListNotFoundError(Messages.LIST_NOT_FOUND.format(name=list_name))
            
            item = item.strip()
            
            if item not in self.lists[actual_list_name]:
                raise ItemNotFoundError(Messages.ITEM_NOT_FOUND.format(item=item, list_name=actual_list_name))
            
            self.lists[actual_list_name].remove(item)
            self._save_data()
            
            logger.info(f"Removed '{item}' from '{actual_list_name}'")
            return Messages.ITEM_REMOVED.format(item=item, list_name=actual_list_name)
            
        except (ListNotFoundError, ItemNotFoundError) as e:
            logger.warning(f"Failed to remove item '{item}' from '{list_name}': {e}")
            return str(e)
        except Exception as e:
            logger.error(f"Unexpected error removing item '{item}' from '{list_name}': {e}")
            return f"❌ An error occurred while removing the item"
    
    def show_list(self, list_name: str) -> str:
        """
        Show items in a specific list.
        
        Args:
            list_name: Name of the list to show
            
        Returns:
            Formatted list content or error message
        """
        try:
            actual_list_name = self._find_list_name(list_name)
            if not actual_list_name:
                raise ListNotFoundError(Messages.LIST_NOT_FOUND.format(name=list_name))
            
            items = self.lists[actual_list_name]
            if not items:
                return Messages.EMPTY_LIST.format(name=actual_list_name)
            
            result = f"📋 **{actual_list_name}** ({len(items)} items):\n"
            for i, item in enumerate(items, 1):
                result += f"{i}. {item}\n"
            
            return result.strip()
            
        except ListNotFoundError as e:
            logger.warning(f"Failed to show list '{list_name}': {e}")
            return str(e)
        except Exception as e:
            logger.error(f"Unexpected error showing list '{list_name}': {e}")
            return f"❌ An error occurred while showing the list"
    
    def show_all_lists(self) -> str:
        """
        Show all available lists.
        
        Returns:
            Formatted list of all lists
        """
        if not self.lists:
            return Messages.NO_LISTS
        
        result = "📚 **All Lists:**\n"
        # Sort lists by name for consistent display
        sorted_lists = sorted(self.lists.items())
        for list_name, items in sorted_lists:
            result += f"• {list_name} ({len(items)} items)\n"
        
        return result.strip()
    
    def delete_list(self, list_name: str) -> str:
        """
        Delete a list.
        
        Args:
            list_name: Name of the list to delete
            
        Returns:
            Success or error message
        """
        try:
            actual_list_name = self._find_list_name(list_name)
            if not actual_list_name:
                raise ListNotFoundError(Messages.LIST_NOT_FOUND.format(name=list_name))
            
            del self.lists[actual_list_name]
            self._save_data()
            
            logger.info(f"Deleted list: {actual_list_name}")
            return Messages.LIST_DELETED.format(name=actual_list_name)
            
        except ListNotFoundError as e:
            logger.warning(f"Failed to delete list '{list_name}': {e}")
            return str(e)
        except Exception as e:
            logger.error(f"Unexpected error deleting list '{list_name}': {e}")
            return f"❌ An error occurred while deleting the list"
    
    def search_item(self, search_term: str) -> str:
        """
        Search for an item across all lists.
        
        Args:
            search_term: Term to search for
            
        Returns:
            Formatted search results or error message
        """
        try:
            if not search_term or not search_term.strip():
                raise ValidationError("Search term cannot be empty")
            
            search_term = search_term.strip()
            results = []
            search_term_lower = search_term.lower()
            
            for list_name, items in self.lists.items():
                for item in items:
                    if search_term_lower in item.lower():
                        results.append(f"📋 {list_name}: {item}")
            
            if not results:
                return Messages.NO_SEARCH_RESULTS.format(term=search_term)
            
            result = f"🔍 **Search results for '{search_term}':**\n"
            result += "\n".join(results)
            return result
            
        except ValidationError as e:
            logger.warning(f"Search validation error: {e}")
            return str(e)
        except Exception as e:
            logger.error(f"Unexpected error searching for '{search_term}': {e}")
            return f"❌ An error occurred while searching"
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics about the lists.
        
        Returns:
            Dictionary with statistics
        """
        total_items = sum(len(items) for items in self.lists.values())
        return {
            'total_lists': len(self.lists),
            'total_items': total_items,
            'average_items_per_list': total_items / len(self.lists) if self.lists else 0,
            'largest_list_size': max(len(items) for items in self.lists.values()) if self.lists else 0,
        }
    
    def get_help(self) -> str:
        """Get help text with available commands."""
        return """🤖 **List Bot Commands:**

**List Management:**
• `create <list_name>` - Create a new list
• `lists` - Show all lists
• `delete <list_name>` - Delete a list

**Item Management:**
• `add <list_name> <item>` - Add item to list
• `remove <list_name> <item>` - Remove item from list
• `show <list_name>` - Show all items in list

**Quick Add (Mention Bot):**
• `@meowlister_bot <list_name> <item1>, <item2>, <item3>` - Add multiple items at once
• `@meowlister_bot groceries milk, bread, eggs` - Example: add 3 items to groceries

**Search:**
• `search <term>` - Search for items across all lists

**Examples:**
• `create groceries`
• `add groceries milk`
• `@meowlister_bot groceries bread, eggs, butter`
• `show groceries`
• `search milk`

**Limits:**
• Max lists: {max_lists}
• Max items per list: {max_items}
• Max list name length: {max_name_len}
• Max item length: {max_item_len}""".format(
            max_lists=self.config.max_lists_per_user,
            max_items=self.config.max_items_per_list,
            max_name_len=self.config.max_list_name_length,
            max_item_len=self.config.max_item_length
        ) 