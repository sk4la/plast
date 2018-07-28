# -*- coding: utf-8 -*-

__all__ = [
    "CharacterEncoding",
    "InvalidObject",
    "InvalidPackage",
    "MalformatedData",
    "ModuleInheritance",
    "NotFound",
    "SystemNotSupported",
    "UnsupportedType"
]

class CustomException(Exception):
    """Generic plast exception"""

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

class CharacterEncoding(CustomException):
    pass

class InvalidObject(CustomException):
    pass

class InvalidPackage(CustomException):
    pass

class MalformatedData(CustomException):
    pass

class ModuleInheritance(CustomException):
    pass

class NotFound(CustomException):
    pass

class SystemNotSupported(CustomException):
    pass

class UnsupportedType(CustomException):
    pass

class UnknownType(CustomException):
    pass
