# backend/app/services/redis.py
import redis
import json
import logging # Use logging

from app.core.redis import redis_client # Assuming this path is correct
# Import custom exceptions
from app.core.exceptions import (
    RedisServiceUnavailableError,
    DataNotFoundError,
    InvalidDataFormatError,
    RedisOperationError
)

logger = logging.getLogger(__name__)

def get_latest_bus_data() -> list: # Add return type hint
    """
    Retrieves the latest bus data list from Redis.

    Raises:
        RedisServiceUnavailableError: If Redis client is not connected.
        DataNotFoundError: If the 'latest_bus_data' key is not found.
        InvalidDataFormatError: If data is found but not a valid JSON list.
        RedisOperationError: If a Redis command fails.

    Returns:
        list: The list of bus data.
    """
    if not redis_client:
        logger.error("Redis client is not available.")
        # Raise specific custom exception
        raise RedisServiceUnavailableError("Serviço Redis indisponível")
    try:
        stored_data = redis_client.get('latest_bus_data')
        if stored_data:
            try:
                full_bus_list = json.loads(stored_data)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON data from Redis: {e}")
                # Raise specific custom exception
                raise InvalidDataFormatError("Erro ao decodificar dados armazenados do Redis.")

            if not isinstance(full_bus_list, list):
                logger.error(f"Invalid data format retrieved from Redis (expected list, got {type(full_bus_list)}).")
                # Raise specific custom exception
                raise InvalidDataFormatError("Formato de dados armazenados inválido (não é uma lista)")
            return full_bus_list
        else:
            logger.info("Key 'latest_bus_data' not found in Redis.")
            # Raise specific custom exception
            raise DataNotFoundError("Dados de ônibus ainda não disponíveis no cache")
    except redis.exceptions.RedisError as e:
        logger.error(f"Redis error during GET operation: {e}")
        # Raise specific custom exception, wrapping original
        raise RedisOperationError(original_exception=e)
    except Exception as e:
        # Catch unexpected errors during this process
        logger.exception(f"Unexpected error in get_latest_bus_data: {e}")
        raise # Re-raise unexpected exceptions or wrap in a generic ServiceError