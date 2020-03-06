from django.http import JsonResponse

from django_serializer.swagger.base import Swagger


def index(request):
    swagger = Swagger()
    swagger.generate()
    return JsonResponse(swagger.spec)
