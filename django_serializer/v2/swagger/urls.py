from django.urls import path

from django_serializer.swagger import views

urlpatterns = [
    path('', views.index, name='swagger')
]
