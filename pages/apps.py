from django.apps import AppConfig

class PagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pages"
    verbose_name = "KSS Merzifon"

    def ready(self):
        # signals'ı burada import et ki kayıt olsun
        from . import signals  # noqa: F401
