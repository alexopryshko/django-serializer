from typing import Sequence

from .base import SerializerException


class IncorrectMetaException(SerializerException):
    def __init__(self, clazz: str, errors: Sequence[str]):
        self.clazz = clazz
        self.errors = errors

    def __str__(self):
        errors = '\n'.join(map(lambda s: f'* {s}', self.errors))
        return f'Meta class of {self.clazz} is incorrect \n{errors}'

    def __repr__(self):
        return self.__str__()


class IncorrectSettingsException(SerializerException):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return f'setting is incorrect: {self.msg}'

    def __repr__(self):
        return self.__str__()
