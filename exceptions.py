"""
Custom exceptions for the List Bot
"""


class ListBotException(Exception):
    """Base exception for List Bot errors"""
    pass


class ValidationError(ListBotException):
    """Raised when input validation fails"""
    pass


class ListNotFoundError(ListBotException):
    """Raised when a requested list doesn't exist"""
    pass


class ListExistsError(ListBotException):
    """Raised when trying to create a list that already exists"""
    pass


class ItemNotFoundError(ListBotException):
    """Raised when a requested item doesn't exist in a list"""
    pass


class ItemExistsError(ListBotException):
    """Raised when trying to add an item that already exists"""
    pass


class LimitExceededError(ListBotException):
    """Raised when a limit is exceeded (too many lists, items, etc.)"""
    pass


class DataStorageError(ListBotException):
    """Raised when there's an error with data storage/retrieval"""
    pass 