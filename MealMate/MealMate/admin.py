from django.apps import apps
from django.contrib import admin

for model in apps.get_models():
    print(f"Registering model: {model.__name__}")
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        print(f"Model already registered: {model.__name__}")