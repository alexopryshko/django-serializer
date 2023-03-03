from django.urls import path

from . import views
from . import generic_views

urlpatterns = [
    path('get', views.GetView.as_view()),
    path('get_query', views.GetQueryView.as_view()),
    path('post', views.PostView.as_view()),
    path('post_body', views.PostBodyView.as_view()),
    path('500', views.InternalServerErrorView.as_view()),
    path('serializer', views.SerializerView.as_view()),
    path('serializer_many', views.SerializerManyView.as_view()),
    # generics
    path('create', generic_views.SomeModelCreateView.as_view()),
    path('get_model', generic_views.SomeModelGetView.as_view()),
    path('update', generic_views.SomeModelUpdateView.as_view()),
    path('delete', generic_views.SomeModelDeleteView.as_view()),
    path('list', generic_views.SimpleListApiView.as_view()),
    path('paginate_list', generic_views.PaginateListApiView.as_view()),
    path('limit_offset_paginate_list', generic_views.LimitOffsetPaginateListApiView.as_view()),
]
