import importlib

from django.apps import AppConfig
from django.conf import settings
from django.urls import path

from django_serializer.v2.swagger import views


class DjangoSerializer(AppConfig):
    name = 'django_serializer'

    def ready(self):
        urls = importlib.import_module(settings.ROOT_URLCONF)
        swagger_url = getattr(settings, 'SWAGGER_URL', 'swagger.json')
        urls.urlpatterns.append(path(swagger_url, views.index))
