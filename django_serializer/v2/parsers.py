import json
from json import JSONDecodeError

from django_serializer.v2.exceptions import ParseException


class BaseParser:
    """
    Base class for any parser.

    Can be extended to use custom parsing logic.
    Do it to use custom json parsing library such as orjson or ultrajson
    """

    def parse(self, data: bytes):
        """
        Implemented in subclass. If you cannot parse data raise ParseException

        :param data: bytes from request.body
        :return: Return something readable inside view. Usually it is dictionary
        """
        raise NotImplementedError


class JsonParser(BaseParser):
    """
    Parses using standard json library.
    """

    def parse(self, data: bytes):
        try:
            return json.loads(data)
        except JSONDecodeError:
            raise ParseException
