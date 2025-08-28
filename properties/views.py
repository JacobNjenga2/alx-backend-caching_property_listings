from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.core import serializers
from .models import Property
from .utils import get_all_properties


@cache_page(60 * 15)  # Cache for 15 minutes
def property_list(request):
    """
    View to list all properties with multi-level Redis caching:
    1. View-level caching (15 minutes) via @cache_page decorator
    2. Low-level queryset caching (1 hour) via get_all_properties()
    
    Returns JSON response with all property data.
    """
    # Use low-level cached queryset (1 hour cache)
    properties = get_all_properties()
    
    # Convert properties to a list of dictionaries for JSON response
    properties_data = []
    for property in properties:
        properties_data.append({
            'id': property.id,
            'title': property.title,
            'description': property.description,
            'price': str(property.price),  # Convert Decimal to string for JSON
            'location': property.location,
            'created_at': property.created_at.isoformat(),
        })
    
    return JsonResponse({
        'properties': properties_data,
        'count': len(properties_data),
        'cached': True,  # Indicator that this response can be cached
    })


# Alternative HTML template-based view (also cached)
@cache_page(60 * 15)  # Cache for 15 minutes
def property_list_html(request):
    """
    HTML template-based view for property listing with multi-level caching:
    1. View-level caching (15 minutes) via @cache_page decorator
    2. Low-level queryset caching (1 hour) via get_all_properties()
    """
    # Use low-level cached queryset (1 hour cache)
    properties = get_all_properties()
    context = {
        'properties': properties,
        'cached_view': True,
    }
    return render(request, 'properties/property_list.html', context)
