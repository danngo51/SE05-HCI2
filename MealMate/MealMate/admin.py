from django.apps import apps
from django.contrib import admin

# Automatically register all models across all apps
for app in apps.get_app_configs():
    for model_name, model in app.models.items():
        try:
            admin.site.register(model)
        except admin.sites.AlreadyRegistered:
            pass