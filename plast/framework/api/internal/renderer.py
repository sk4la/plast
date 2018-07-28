# -*- coding: utf-8 -*-

from framework.contexts import errors as _errors
from framework.contexts.logger import Logger as _log

try:
    import simplejson as json

except ImportError as exc:
    _log.fault("Missing dependency <{0}>. Try <pip install {0}> or manually build the required module to fix the issue.".format(exc.name))

__all__ = [
    "Renderer"
]

class Renderer:
    """Helper class for specific formatting and rendering."""

    @staticmethod
    def from_json(data):
        """
        .. py:function:: from_json(data)

        Renders JSON-encoded data as a Python dictionary.

        :param data: JSON-encoded data to render
        :type data: str

        :return: dictionary translation of :code:`data`
        :rtype: dict

        :raises CharacterEncoding: if :code:`data` cannot be decoded
        :raises InvalidObject: if :code:`data` is malformated
        """

        try:
            return json.loads(data)

        except UnicodeDecodeError:
            raise _errors.CharacterEncoding

        except (
            OverflowError,
            TypeError,
            ValueError,
            Exception):

            raise _errors.InvalidObject

    @staticmethod
    def to_json(data, indent=None):
        """
        .. py:function:: to_json(data)

        Renders a Python dictionary as JSON-encoded data.

        :param data: data to render
        :type data: dict

        :param indent: number of spaces for indentation
        :type indent: int

        :return: JSON-encoded translation of :code:`data`
        :rtype: str

        :raises CharacterEncoding: if :code:`data` cannot be encoded
        :raises InvalidObject: if :code:`data` is malformated
        """

        try:
            return json.dumps(data, sort_keys=True, indent=(indent if indent else None))

        except UnicodeDecodeError:
            raise _errors.CharacterEncoding

        except (
            OverflowError,
            TypeError,
            ValueError,
            Exception):

            raise _errors.InvalidObject
