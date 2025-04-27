class ServiceError(Exception):
    """Base class for service layer exceptions."""
    pass

class RedisServiceUnavailableError(ServiceError):
    """Raised when the Redis client is not available."""
    pass

class DataNotFoundError(ServiceError):
    """Raised when requested data is not found (e.g., key missing in Redis)."""
    pass

class InvalidDataFormatError(ServiceError):
    """Raised when data retrieved has an unexpected format."""
    pass

class RedisOperationError(ServiceError):
    """Raised for underlying Redis client errors."""
    def __init__(self, message="Redis operation failed", original_exception=None):
        super().__init__(message)
        self.original_exception = original_exception