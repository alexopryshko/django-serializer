from django.http import JsonResponse

from django_serializer.v2.swagger.base import Swagger


def index(request):
    swagger = Swagger()
    swagger.generate()
    response = JsonResponse(swagger.spec)
    response['Access-Control-Allow-Origin'] = "*"
    response['Access-Control-Allow-Methods'] = "GET, OPTIONS"
    return response
