# Django-serializer

## Installation

django-serializer packaged and delivered via [pypi](https://pypi.org/project/django-serializer/)

`pip install django-serializer`

## Features
Serialization provided by [marshmallow](https://github.com/marshmallow-code/marshmallow).
The library provide generic and custom CRUD views and paginators.
Automatic swagger generation provided by [apispec](https://github.com/marshmallow-code/apispec)

# Changelog
See [HISTORY.md](https://github.com/alexopryshko/django-serializer/blob/master/HISTORY.md)

## Quickstart

### basic flow
```python
from django_serializer.v2.serializer import ModelSerializer
from django_serializer.v2.views import ApiView 
from myapp.models import MyModel

class MyModelSerializer(ModelSerializer):
    class SMeta:
        model = MyModel
        fields = ('id', 'foo', 'bar')

class MyView(ApiView):
    class Meta:
        serializer = MyModelSerializer

    def execute(self, request, *args, **kwargs):
        return MyModel.objects.first()
```

### multiple objects
```python
from django_serializer.v2.serializer import ModelSerializer
from django_serializer.v2.views import ApiView 
from myapp.models import MyModel

class MyModelSerializer(ModelSerializer):
    class SMeta:
        model = MyModel
        fields = ('id', 'foo', 'bar')

class MyListView(ApiView):
    class Meta:
        serializer = MyModelSerializer
        serializer_many = True

    def execute(self, request, *args, **kwargs):
        return MyModel.objects.first()
```

### using query params
```python
from django import forms
from django_serializer.v2.views import ApiView 

class MyQueryForm(forms.Form):
    id = forms.IntegerField() 

class MyListView(ApiView):
    class Meta:
        query_form = MyQueryForm
        serializer = MyModelSerializer
        serializer_many = True
        
    def execute(self, request, *args, **kwargs):
        object_id = self.request_query['id']
        return MyModel.objects.filter(id=object_id).first()
```

### add swagger
```python
# urls.py
from django_serializer.v2.swagger.views import index
from django.urls import path

urlpatterns = [
    path('swagger.json', index),
]
```


## Contribution
Feel free to open pull request to the latest `rc-<version>` branch.

## Licence 
See [LICENSE](https://github.com/alexopryshko/django-serializer/blob/master/LICENSE.txt)