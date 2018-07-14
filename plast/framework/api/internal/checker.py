# -*- coding: utf-8 -*-

from framework.api.external import filesystem as _fs

from framework.contexts import errors as _errors
from framework.contexts.configuration import Configuration as _conf
from framework.contexts.meta import Meta as _meta

import os.path
import platform
import types

__all__ = [
    "Checker"
]

class Checker:
    """Assists data check."""

    @staticmethod
    def sanitize_data(data):
        """
        .. py:function:: sanitize_data(data)

        Strips non white-listed characters in :code:`data`.

        :param data: input data to sanitize
        :type data: str

        :return: sanitized representation of :code:`data`
        :rtype: str

        :raises MalformatedData: if :code:`data` cannot be decoded correctly
        """

        try:
            return (str().join(_ for _ in data.decode("utf-8").strip() if _.isalnum())).strip()

        except AttributeError:
            try:
                return (str().join(_ for _ in data.strip() if _.isalnum())).strip()

            except Exception:
                raise _errors.MalformatedDataError

        except Exception:
            raise _errors.MalformatedDataError

    @staticmethod
    def number_rulesets(directory=os.path.join(_meta.__root__, "rulesets"), globbing_filters=_conf.YARA_EXTENSION_FILTERS):
        """
        .. py:function:: number_rulesets(directory=os.path.join(_meta.__root__, "rulesets"), globbing_filters=_conf.YARA_EXTENSION_FILTERS)

        Returns the total number of YARA ruleset(s).

        :param directory: absolute path to the rulesets directory
        :type directory: str

        :param globbing_filters: list of globbing filter(s) to apply for the search
        :type globbing_filters: list

        :return: number of YARA ruleset(s) in :code:`directory`
        :rtype: int
        """

        return sum(1 for _ in _fs.enumerate_matching_files(directory, globbing_filters, recursive=True))

    @staticmethod
    def check_package(package):
        """
        .. py:function:: check_package(package)

        Checks whether package is a valid Python package.

        :param package: handle to a Python package
        :type package: class

        :raises InvalidPackageError: if the package is not a valid Python package
        """

        if not isinstance(package, types.ModuleType):
            raise _errors.InvalidPackageError

    @staticmethod
    def check_module(object, model):
        """
        .. py:function:: check_module(object, model)

        Checks whether :code:`object` is a valid module.

        :param object: module class handle
        :type object: class

        :param model: reference module class handle
        :type model: class

        :raises NotFoundError: if no subclass of one of the reference models can be found in :code:`object`
        :raises ModuleInheritanceError: if the class found in :code:`object` does not inherit from the reference model
        :raises SystemNotSupportedError: if the module does not support the current system
        """

        if not hasattr(object, model.__name__):
            raise _errors.NotFoundError

        if not issubclass(getattr(object, model.__name__), model):
            raise _errors.ModuleInheritanceError

        if platform.system() not in getattr(getattr(object, model.__name__, None), "__system__", []):
            raise _errors.SystemNotSupportedError
