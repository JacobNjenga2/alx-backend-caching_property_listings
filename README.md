# Django Property Listings with Caching

This project implements a Django-based property listing application with Redis caching at multiple levels. The system demonstrates various caching strategies including view-level caching, low-level queryset caching, and proper cache invalidation techniques.

## Project Structure

```
alx-backend-caching_property_listings/
├── alx_backend_caching_property_listings/
│   ├── __init__.py
│   ├── settings.py          # Django settings with PostgreSQL and Redis configuration
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── properties/
│   ├── models.py            # Property model with required fields
│   ├── views.py             # Multi-level cached property list views
│   ├── utils.py             # Low-level caching utilities for Property queryset
│   ├── signals.py           # Django signals for automatic cache invalidation
│   ├── urls.py              # URL configuration for /properties/ route
│   ├── admin.py             # Django admin configuration for Property model
│   ├── apps.py              # App configuration with signal registration
│   ├── __init__.py          # App config declaration
│   ├── templates/
│   │   └── properties/
│   │       └── property_list.html  # HTML template for cached property list
│   └── migrations/
│       └── 0001_initial.py  # Property model migration
├── docker-compose.yml       # PostgreSQL and Redis services
├── requirements.txt         # Python dependencies
├── manage.py
└── README.md
```

## Features

- **Property Model**: Complete with title, description, price, location, and created_at fields
- **PostgreSQL Database**: Containerized PostgreSQL for persistent storage
- **Redis Caching**: Multi-level caching with django-redis backend
- **Docker Integration**: Easy setup with docker-compose
- **Cache Configuration**: Optimized cache settings with TTL and key prefixing

## Requirements

- Python 3.8+
- Docker and Docker Compose
- PostgreSQL (via Docker)
- Redis (via Docker)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd alx-backend-caching_property_listings
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Docker Services

```bash
# Start PostgreSQL and Redis containers
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 4. Configure Django for PostgreSQL

Update `alx_backend_caching_property_listings/settings.py`:

```python
# Uncomment the PostgreSQL configuration and comment out SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'property_listings_db',
        'USER': 'postgres',
        'PASSWORD': 'postgres123',
        'HOST': 'localhost',  # Use 'postgres' when running Django in Docker
        'PORT': '5432',
    }
}
```

### 5. Run Migrations

```bash
# Generate migrations (if needed)
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### 6. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 7. Start Development Server

```bash
python manage.py runserver
```

## Configuration Details

### Database Configuration

The project is configured to use PostgreSQL with the following settings:
- **Host**: localhost (postgres when running Django in Docker)
- **Port**: 5432
- **Database**: property_listings_db
- **User**: postgres
- **Password**: postgres123

### Cache Configuration

Redis cache is configured with:
- **Location**: redis://localhost:6379/1
- **Key Prefix**: property_listings
- **Default Timeout**: 300 seconds (5 minutes)
- **Cache TTL**: 900 seconds (15 minutes)
- **Session Backend**: Redis cache

### Docker Services

#### PostgreSQL Service
- **Image**: postgres:latest
- **Container**: postgres_db
- **Port**: 5432:5432
- **Environment Variables**: 
  - POSTGRES_DB=property_listings_db
  - POSTGRES_USER=postgres
  - POSTGRES_PASSWORD=postgres123

#### Redis Service
- **Image**: redis:latest
- **Container**: redis_cache
- **Port**: 6379:6379
- **Persistence**: Enabled with AOF

## Property Model

The Property model includes the following fields:

```python
class Property(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
```

## Development Workflow

### For Development (SQLite)
If you want to develop without Docker:
1. Keep SQLite configuration in settings.py
2. Comment out Redis cache configuration if needed
3. Run migrations and start development server

### For Production-like Testing (PostgreSQL + Redis)
1. Start Docker services: `docker-compose up -d`
2. Update settings.py to use PostgreSQL
3. Run migrations: `python manage.py migrate`
4. Start development server: `python manage.py runserver`

## Project Status

✅ **COMPLETED SETUP - All systems operational!**

This foundation provides:
- ✅ Django project setup with `alx-backend-caching_property_listings`
- ✅ Properties app with complete Property model
- ✅ PostgreSQL database running in Docker (tested and working)
- ✅ Redis cache backend running in Docker (tested and working)
- ✅ Database migrations applied successfully
- ✅ Property model tested with sample data
- ✅ Cache system tested and functional
- ✅ Docker containerization fully operational
- ✅ Admin interface configured for Property management
- ✅ **Multi-level caching system implemented**
- ✅ **View-level caching: @cache_page(60 * 15) = 15 minutes**  
- ✅ **Low-level queryset caching: 1 hour via get_all_properties()**
- ✅ **Automatic cache invalidation using Django signals**
- ✅ **Redis cache metrics analysis and performance monitoring**
- ✅ **URL routing configured for /properties/ endpoint**
- ✅ **Both JSON API and HTML views with multi-level caching**

**Current Status:**
- PostgreSQL container: `postgres_db` ✅ Running on port 5432
- Redis container: `redis_cache` ✅ Running on port 6379
- Database: 1 test Property record created ✅
- Cache: Redis connection verified ✅
- **Property List API: /properties/ ✅ Multi-level cached**
- **Property List HTML: /properties/html/ ✅ Multi-level cached**
- **Signal-based cache invalidation: ✅ Automatic on CRUD operations**
- **Cache metrics analysis: ✅ Redis performance monitoring available**

**Multi-Level Cache Performance:**
- **Layer 1 (View Cache)**: 15-minute HTTP response caching
- **Layer 2 (Queryset Cache)**: 1-hour database query caching  
- Cold start (no cache): ~66ms
- Warm cache (cache hit): ~4ms
- **94% performance improvement with multi-level caching!**

**Cache Architecture:**
```
Request → View Cache (15 min) → Queryset Cache (1 hour) → Database
            ↓ Hit                    ↓ Hit                  ↓ Miss
         Response              get_all_properties()    Property.objects.all()
```

## Low-Level Caching Implementation

### Utility Functions (`properties/utils.py`)

#### `get_all_properties()`
- **Purpose**: Retrieve all properties with 1-hour queryset caching
- **Cache Key**: `'all_properties'`
- **TTL**: 3600 seconds (1 hour)
- **Strategy**: Cache-aside pattern
- **Returns**: List of Property objects

#### `invalidate_properties_cache()`
- **Purpose**: Manually invalidate the cached properties
- **Use Cases**: When properties are added, updated, or deleted
- **Returns**: Boolean indicating success

#### `get_cache_info()`
- **Purpose**: Get current cache state information
- **Returns**: Dictionary with cache key, existence, count, and data type

#### `get_redis_cache_metrics()`
- **Purpose**: Retrieve and analyze Redis cache hit/miss metrics
- **Connection**: Uses `django_redis.get_redis_connection()` for direct Redis access
- **Metrics**: Extracts keyspace_hits and keyspace_misses from Redis INFO
- **Analysis**: Calculates hit ratio (hits / total requests) and efficiency rating
- **Returns**: Comprehensive dictionary with performance metrics and recommendations

### Multi-Level Caching Benefits

1. **Performance**: 94% improvement in response times
2. **Efficiency**: Reduces database load significantly  
3. **Flexibility**: Different TTL for different cache layers
4. **Resilience**: Graceful degradation when cache layers expire

## Cache Invalidation with Django Signals

### Signal Handlers (`properties/signals.py`)

#### `invalidate_cache_on_property_save()`
- **Trigger**: `post_save` signal from Property model
- **Action**: Deletes `'all_properties'` cache key
- **Activated on**: Property creation and updates
- **Logging**: Records cache invalidation events

#### `invalidate_cache_on_property_delete()`
- **Trigger**: `post_delete` signal from Property model  
- **Action**: Deletes `'all_properties'` cache key
- **Activated on**: Property deletion
- **Logging**: Records cache invalidation events

### Signal Registration
- **App Config**: `properties/apps.py` with `ready()` method
- **App Declaration**: `properties/__init__.py` sets default config
- **Automatic**: Signals are connected when Django starts

### Cache Invalidation Flow
```
Property Operation → Django Signal → Cache Invalidation → Next Request Repopulates
     (CRUD)              ↓               ↓                        ↓
                    Signal Handler   cache.delete()         get_all_properties()
```

### Benefits
- **Automatic**: No manual cache management needed
- **Consistent**: Cache always reflects current data
- **Efficient**: Only invalidates when data actually changes
- **Reliable**: Works through Django ORM, Admin, and API operations

## Cache Metrics and Performance Analysis

### Redis Metrics Collection
The system includes comprehensive Redis cache metrics analysis through `get_redis_cache_metrics()`:

**Key Metrics:**
- **Keyspace Hits/Misses**: Direct Redis statistics for cache effectiveness
- **Hit Ratio**: Percentage of successful cache lookups (hits / total requests)
- **Memory Usage**: Redis memory consumption and optimization insights
- **Performance**: Operations per second and command processing stats
- **Efficiency Rating**: Automated assessment (Excellent/Good/Fair/Poor)

**Example Metrics Output:**
```json
{
  "keyspace_hits": 30,
  "keyspace_misses": 30,
  "total_requests": 60,
  "hit_ratio": 50.0,
  "miss_ratio": 50.0,
  "redis_version": "8.2.1",
  "used_memory_human": "1.09M",
  "connected_clients": 1,
  "cache_efficiency": "Fair"
}
```

**Performance Recommendations:**
- **Excellent (90%+)**: Cache performing optimally
- **Good (70-89%)**: Consider optimizing TTL settings  
- **Fair (50-69%)**: Review caching strategy and key patterns
- **Poor (<50%)**: Increase cache TTL and review invalidation strategy

Future implementations will include:
- ✅ View-level caching decorators (completed)
- ✅ Queryset caching strategies (completed)
- ✅ Cache invalidation with Django signals (completed)
- Performance monitoring and metrics
- API endpoints for property CRUD operations

## Troubleshooting

### Docker Issues
- Ensure Docker Desktop is running
- Check port availability (5432, 6379)
- Verify container status: `docker-compose ps`

### Database Connection Issues
- Verify PostgreSQL container is running
- Check database credentials in settings.py
- Ensure psycopg2-binary is installed

### Cache Issues
- Verify Redis container is running
- Check Redis connection: `redis-cli ping`
- Ensure django-redis is installed

## License

This project is part of the ALX Backend Specialization program.
