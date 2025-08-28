"""
Utility functions for property caching and data management.

This module implements low-level caching strategies for Property querysets
using Django's cache framework with Redis backend.
"""

from django.core.cache import cache
from django_redis import get_redis_connection
from .models import Property
import logging

# Set up logging for cache operations
logger = logging.getLogger(__name__)

def get_all_properties():
    """
    Retrieve all properties with low-level caching.
    
    This function implements a cache-aside pattern:
    1. Check Redis cache for 'all_properties' key
    2. If cache miss, fetch from database
    3. Store result in cache for 1 hour (3600 seconds)
    4. Return the queryset
    
    Returns:
        QuerySet: All Property objects ordered by creation date (newest first)
    """
    cache_key = 'all_properties'
    
    # Try to get data from cache first
    cached_properties = cache.get(cache_key)
    
    if cached_properties is not None:
        logger.info(f"Cache HIT for key '{cache_key}' - returning cached properties")
        return cached_properties
    
    # Cache miss - fetch from database
    logger.info(f"Cache MISS for key '{cache_key}' - fetching from database")
    
    # Fetch all properties from database
    properties_queryset = Property.objects.all().order_by('-created_at')
    
    # Convert queryset to list to make it serializable for caching
    # Note: We cache the evaluated queryset (list) rather than the lazy queryset
    properties_list = list(properties_queryset)
    
    # Store in cache for 1 hour (3600 seconds)
    cache.set(cache_key, properties_list, 3600)
    logger.info(f"Cached {len(properties_list)} properties for 1 hour")
    
    return properties_list


def invalidate_properties_cache():
    """
    Invalidate the cached properties when data changes.
    
    This function should be called when:
    - New properties are added
    - Existing properties are updated
    - Properties are deleted
    
    Returns:
        bool: True if cache was successfully deleted, False otherwise
    """
    cache_key = 'all_properties'
    
    result = cache.delete(cache_key)
    if result:
        logger.info(f"Successfully invalidated cache for key '{cache_key}'")
    else:
        logger.warning(f"Failed to invalidate cache for key '{cache_key}' (may not exist)")
    
    return result


def get_cache_info():
    """
    Get information about the current cache state for properties.
    
    Returns:
        dict: Cache information including key existence and TTL
    """
    cache_key = 'all_properties'
    
    # Check if key exists in cache
    cached_data = cache.get(cache_key)
    exists = cached_data is not None
    
    info = {
        'cache_key': cache_key,
        'exists': exists,
        'count': len(cached_data) if exists else 0,
        'data_type': type(cached_data).__name__ if exists else None,
    }
    
    return info


def get_redis_cache_metrics():
    """
    Retrieve and analyze Redis cache hit/miss metrics.
    
    Connects to Redis via django_redis, gets keyspace_hits and keyspace_misses
    from INFO command, calculates hit ratio, and returns comprehensive metrics.
    
    Returns:
        dict: Dictionary containing cache metrics including:
            - keyspace_hits: Number of successful key lookups
            - keyspace_misses: Number of failed key lookups  
            - total_requests: Total cache requests
            - hit_ratio: Hit rate as percentage (0-100)
            - miss_ratio: Miss rate as percentage (0-100)
            - redis_info: Additional Redis server information
    """
    try:
        # Get Redis connection via django_redis
        redis_connection = get_redis_connection("default")
        
        # Get Redis INFO statistics
        redis_info = redis_connection.info()
        
        # Extract keyspace statistics
        keyspace_hits = redis_info.get('keyspace_hits', 0)
        keyspace_misses = redis_info.get('keyspace_misses', 0)
        total_requests = keyspace_hits + keyspace_misses
        
        # Calculate hit ratio
        hit_ratio = (keyspace_hits / total_requests) * 100 if total_requests > 0 else 0
        miss_ratio = (keyspace_misses / total_requests) * 100 if total_requests > 0 else 0
        
        # Prepare metrics dictionary
        metrics = {
            'keyspace_hits': keyspace_hits,
            'keyspace_misses': keyspace_misses,
            'total_requests': total_requests,
            'hit_ratio': round(hit_ratio, 2),
            'miss_ratio': round(miss_ratio, 2),
            'redis_version': redis_info.get('redis_version', 'Unknown'),
            'used_memory': redis_info.get('used_memory', 0),
            'used_memory_human': redis_info.get('used_memory_human', '0B'),
            'connected_clients': redis_info.get('connected_clients', 0),
            'total_commands_processed': redis_info.get('total_commands_processed', 0),
            'instantaneous_ops_per_sec': redis_info.get('instantaneous_ops_per_sec', 0),
            'cache_efficiency': 'Excellent' if hit_ratio >= 90 else 'Good' if hit_ratio >= 70 else 'Fair' if hit_ratio >= 50 else 'Poor'
        }
        
        # Log the metrics
        logger.info(
            f"Redis Cache Metrics - "
            f"Hits: {keyspace_hits}, Misses: {keyspace_misses}, "
            f"Hit Ratio: {hit_ratio:.2f}%, Total Requests: {total_requests}, "
            f"Efficiency: {metrics['cache_efficiency']}"
        )
        
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to retrieve Redis cache metrics: {str(e)}")
        
        # Return default metrics structure with error info
        return {
            'keyspace_hits': 0,
            'keyspace_misses': 0,
            'total_requests': 0,
            'hit_ratio': 0.0,
            'miss_ratio': 0.0,
            'redis_version': 'Unknown',
            'used_memory': 0,
            'used_memory_human': '0B',
            'connected_clients': 0,
            'total_commands_processed': 0,
            'instantaneous_ops_per_sec': 0,
            'cache_efficiency': 'Error',
            'error': str(e)
        }
