from django.apps import AppConfig


class PropertiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'properties'
    
    def ready(self):
        """
        Called when the app is ready.
        Import signals to ensure they are connected when Django starts.
        """
        import properties.signals  # Import signals to register them