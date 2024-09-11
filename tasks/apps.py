from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'

from django.apps import AppConfig
from django.db.models.signals import post_migrate

class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'

    def ready(self):
        # Import the function here to avoid circular imports
        from .views import start_pending_task
        
        # Connect the start_pending_task function to the post_migrate signal
        post_migrate.connect(self.on_post_migrate, sender=self)

    def on_post_migrate(self, sender, **kwargs):
        # This function will be called after migrations are applied
        from .views import start_pending_task
        start_pending_task()