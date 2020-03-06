from django.urls import path

from django_serializer.v2.swagger import views

urlpatterns = [
    path('', views.index, name='swagger')
]
