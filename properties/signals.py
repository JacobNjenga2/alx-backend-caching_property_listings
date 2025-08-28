"""
Django signals for automatic cache invalidation.

This module contains signal handlers that automatically invalidate
the Redis cache when Property model instances are created, updated, or deleted.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Property
import logging

# Set up logging for signal operations
logger = logging.getLogger(__name__)


@receiver(post_save, sender=Property)
def invalidate_cache_on_property_save(sender, instance, created, **kwargs):
    """
    Signal handler for Property post_save.
    
    Invalidates the 'all_properties' cache when a Property is created or updated.
    
    Args:
        sender: The model class (Property)
        instance: The actual instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    cache_key = 'all_properties'
    
    # Delete the cache
    cache_deleted = cache.delete(cache_key)
    
    action = "created" if created else "updated"
    
    if cache_deleted:
        logger.info(
            f"Cache invalidated: Property '{instance.title}' was {action}. "
            f"Cache key '{cache_key}' removed from Redis."
        )
    else:
        logger.info(
            f"Property '{instance.title}' was {action}. "
            f"Cache key '{cache_key}' was not found (may have already expired)."
        )


@receiver(post_delete, sender=Property)
def invalidate_cache_on_property_delete(sender, instance, **kwargs):
    """
    Signal handler for Property post_delete.
    
    Invalidates the 'all_properties' cache when a Property is deleted.
    
    Args:
        sender: The model class (Property)
        instance: The actual instance being deleted
        **kwargs: Additional keyword arguments
    """
    cache_key = 'all_properties'
    
    # Delete the cache
    cache_deleted = cache.delete(cache_key)
    
    if cache_deleted:
        logger.info(
            f"Cache invalidated: Property '{instance.title}' was deleted. "
            f"Cache key '{cache_key}' removed from Redis."
        )
    else:
        logger.info(
            f"Property '{instance.title}' was deleted. "
            f"Cache key '{cache_key}' was not found (may have already expired)."
        )


def manual_cache_invalidation():
    """
    Manual cache invalidation function for testing or administrative purposes.
    
    Returns:
        bool: True if cache was successfully deleted, False otherwise
    """
    cache_key = 'all_properties'
    result = cache.delete(cache_key)
    
    if result:
        logger.info(f"Manual cache invalidation: Cache key '{cache_key}' removed.")
    else:
        logger.warning(f"Manual cache invalidation: Cache key '{cache_key}' not found.")
    
    return result
