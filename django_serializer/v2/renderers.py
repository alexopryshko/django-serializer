from django.http import HttpResponse, JsonResponse

__all__ = ("BaseRenderer", "JsonRenderer")


class BaseRenderer:
    """
    Base class for any renderer
    """

    def render(self, data: dict) -> HttpResponse:
        """
        Implemented in subclasses

        :param data: input dictionary. Usually returned by execute or serializer stage
        :return: HttpResponse instance to answer to HttpRequest
        """
        raise NotImplementedError


class JsonRenderer(BaseRenderer):
    """
    Renders dict to JsonResponse
    """

    def render(self, data: dict) -> HttpResponse:
        return JsonResponse(data=data)
