from django.urls import path

from . import views

urlpatterns = [
    path('get', views.GetView.as_view()),
    path('get_query', views.GetQueryView.as_view()),
    path('post', views.PostView.as_view()),
    path('post_body', views.PostBodyView.as_view()),
    path('500', views.InternalServerErrorView.as_view()),
    path('serializer', views.SerializerView.as_view()),
    path('serializer_many', views.SerializerManyView.as_view()),
]
