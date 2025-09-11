from django.apps import AppConfig


class TestAppConfig(AppConfig):
    """Configuration for the test app."""

    name = 'testapp'
    verbose_name = 'Test App'

    default_auto_field = 'django.db.models.AutoField'
