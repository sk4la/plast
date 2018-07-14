# -*- coding: utf-8 -*-

from framework.contexts.logger import Logger as _log

__all__ = [
    "Callback",
    "Post",
    "Pre"
]

class Callback:
    """Base callback module class."""

    __slots__ = [
        "__author__", 
        "__description__", 
        "__license__",
        "__maintainer__",
        "__system__",
        "__version__"
    ]

    def run(self, data):
        _log.warning("Unimplemented <{}> module.".format(self.__class__.__name__))

class Post:
    """Base postprocessing module class."""

    __slots__ = [
        "__author__", 
        "__description__", 
        "__license__",
        "__maintainer__",
        "__system__",
        "__version__"
    ]

    def run(self, case):
        _log.warning("Unimplemented <{}> module.".format(self.__class__.__name__))

class Pre:
    """Base preprocessing module class."""

    __slots__ = [
        "__author__", 
        "__description__", 
        "__license__",
        "__maintainer__",
        "__system__",
        "__version__"
    ]

    def __init__(self, parser):
        pass

    def run(self):
        _log.warning("Unimplemented <{}> module.".format(self.__class__.__name__))
