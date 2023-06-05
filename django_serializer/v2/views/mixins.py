from typing import Type

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model
from django.http import HttpRequest

from django_serializer.v2.exceptions import (
    NotFoundError,
    AuthRequiredError,
    ForbiddenError,
)


class FormMixin:
    def get_form_kwargs(self):
        kwargs = {}
        if self.request.method in ("POST", "PUT", "PATCH"):
            kwargs.update(
                {
                    "data": self.get_request_json(self.request),
                    "files": self.request.FILES,
                }
            )
        return kwargs

    def get_form_class(self):
        return self.Meta.model_form

    def get_form(self):
        form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs())


class ObjectMixin:
    def _get_object(self):
        if hasattr(self, "_object"):
            return getattr(self, "_object")
        try:
            obj = self.get_object()
            setattr(self, "_object", obj)
            return obj
        except ObjectDoesNotExist:
            raise NotFoundError

    def get_object(self):
        m: Type[Model] = self.Meta.model
        key: str = self.Meta.object_key
        return m.objects.get(**{key: self.request_body[key]})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self._get_object()
        return kwargs


class LoginRequiredMixin:
    """
    Allow request only for authorized user
    """

    def _check_section_permission(self, request: HttpRequest):
        if not request.user.is_authenticated:
            raise AuthRequiredError

        return super()._check_section_permission(request)


class CheckPermissionsMixin:
    def has_permissions(self, **kwargs) -> bool:
        return True

    def check_permissions(self, **kwargs):
        if not self.has_permissions(**kwargs):
            raise ForbiddenError
