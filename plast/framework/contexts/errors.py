# -*- coding: utf-8 -*-

__all__ = [
    "CharacterEncodingError",
    "InvalidObjectError",
    "InvalidPackageError",
    "MalformatedDataError",
    "ModuleInheritanceError",
    "NotFoundError",
    "SystemNotSupportedError",
    "UnsupportedTypeError"
]

class CustomException(Exception):
    """Generic plast exception"""

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

class CharacterEncodingError(CustomException):
    pass

class InvalidObjectError(CustomException):
    pass

class InvalidPackageError(CustomException):
    pass

class MalformatedDataError(CustomException):
    pass

class ModuleInheritanceError(CustomException):
    pass

class NotFoundError(CustomException):
    pass

class SystemNotSupportedError(CustomException):
    pass

class UnsupportedTypeError(CustomException):
    pass
