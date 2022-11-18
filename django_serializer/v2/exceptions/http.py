from .base import ApiViewException

__all__ = (
    'HttpError', 'HttpNotImplementedError', 'BadRequestError',
    'InternalServerError', 'HttpFormError', 'NotFoundError',
    'AuthRequiredError', 'ForbiddenError'
)


class HttpError(ApiViewException):
    def __init__(self, http_code, alias, description):
        self.http_code = http_code
        self.alias = alias
        self.description = description

    def get_dict(self):
        return {
            'status': self.alias,
            'message': self.description,
            'data': {}
        }


class HttpNotImplementedError(HttpError):
    def __init__(self):
        super().__init__(
            http_code=405,
            alias='not_implemented',
            description='Not implemented'
        )


class BadRequestError(HttpError):
    def __init__(self, description='Bad request'):
        super().__init__(
            http_code=400,
            alias='bad_request',
            description=description
        )


class AuthRequiredError(HttpError):
    def __init__(self):
        super().__init__(
            http_code=401,
            alias='auth_required',
            description='Authentication required'
        )


class ForbiddenError(HttpError):
    def __init__(self):
        super().__init__(
            http_code=403,
            alias='forbidden',
            description='Forbidden'
        )


class NotFoundError(HttpError):
    def __init__(self):
        super().__init__(
            http_code=404,
            alias='not_found',
            description='Not Found'
        )


class InternalServerError(HttpError):
    def __init__(self):
        super().__init__(
            http_code=500,
            alias='internal_error',
            description='Internal server error'
        )


class HttpFormError(BadRequestError):
    def __init__(self, form):
        self.form = form
        super().__init__()

        self.field_problems = {}
        for field, error in self.form.errors.items():
            problems = []
            for data_item in error.data:
                for message in data_item.messages:
                    problems.append(message)
            self.field_problems[field] = problems

    def get_dict(self):
        d = super().get_dict()
        d['field_problems'] = self.field_problems
        return d
