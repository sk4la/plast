# -*- coding: utf-8 -*-

from framework.api.internal.renderer import Renderer as _renderer

from framework.contexts import errors as _errors
from framework.contexts.configuration import Configuration as _conf
from framework.contexts.logger import Logger as _log

try:
    import pendulum

except ImportError as exc:
    _log.fault("Missing dependency <{0}>. Try <pip install {0}> or manually build the required module to fix the issue.".format(exc.name))

__all__ = [
    "iterate_matches",
    "timestamp"
]

def iterate_matches(target):
    """
    .. py:function:: iterate_matches(target)

    Iterates over match(es) and yields a Python dictionary representation of each.

    :param target: path to the file containing JSON-encoded match(es)
    :type target: str
    
    :return: dictionary representation of the match
    :rtype: dict
    """

    with open(target) as matches:
        for match in matches:
            try:
                yield _renderer.from_json(match)

            except (
                _errors.CharacterEncoding,
                _errors.InvalidObject):

                _log.error("Failed to interpret match <{}>.".format(match))

def timestamp(formatter=_conf.DEFAULTS["DATETIME_FORMATTER"], timezone=_conf.DEFAULTS["TIMEZONE"]):
    """
    .. py:function:: timestamp(fmt="%Y-%m-%d %H:%M:%S", timezone=_conf.DEFAULTS["TIMEZONE"])

    Generates a string representation of the current time.

    :param formatter: format string used to format the current time
    :type formatter: str

    :param timezone: timezone to render
    :type timezone: str

    :return: string representation of the current time
    :rtype: str
    """

    return pendulum.now(timezone).format(formatter)
