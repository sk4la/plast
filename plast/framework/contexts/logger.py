# -*- coding: utf-8 -*-

from framework.contexts.meta import Meta as _meta

import functools
import logging
import logging.config
import multiprocessing
import sys

__all__ = [
    "Logger"
]

class Logger:
    """Main logger class."""

    _lock = multiprocessing.Lock()

    def _synchronize(destination):
        """
        .. py:function:: _synchronize(destination)

        Synchronizes the file writing operations through :code:`multiprocessing.Lock`.

        :param destination: function to wrap
        :type destination: class

        :return: wrapper function
        :rtype: class
        """

        @functools.wraps(destination)
        def synchronize(*args, **kwargs):
            with Logger._lock:
                destination(*args, **kwargs)

        return synchronize

    try:
        logging.config.dictConfig({
            "version": 1,
            "disable_existing_loggers": True,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s %(levelname)-8s %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                },
                "colored": {
                    "()": "colorlog.ColoredFormatter",
                    "format": "%(asctime)s %(log_color)s%(levelname)-8s%(reset)s %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "reset": True,
                    "log_colors": {
                        "DEBUG": "white",
                        "INFO": "green",
                        "WARNING":"yellow",
                        "ERROR": "red",
                        "CRITICAL": "red"
                    }
                }
            },
            "handlers": {
                "core": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "standard",
                    "level": "DEBUG",
                    "mode": "a",
                    "maxBytes": 1024 * 1024 * 10,
                    "backupCount": 10,
                    "filename": "/var/log/{0}/{0}.log".format(_meta.__package__)
                },
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "colored",
                    "level": "DEBUG"
                }
            },
            "loggers": {
                "core" : {
                    "level": "DEBUG",
                    "handlers": [
                        "core"
                    ]
                },
                "console" : {
                    "level": "DEBUG",
                    "handlers": [
                        "console"
                    ]
                }
            }
        })

    except (
        ModuleNotFound,
        ValueError) as exc:

        sys.exit(exc)

    core = logging.getLogger("core")
    console = logging.getLogger("console")

    @staticmethod
    def _create_file_logger(name, path, level="WARNING", encoding="utf-8"):
        """
        .. py:function:: _create_file_logger(name, path, encoding)

        Creates a default file logger.

        :param name: name of the logger
        :type name: str

        :param path: path to the logging file
        :type path: str

        :param level: logging level for the new logger
        :type level: str

        :param encoding: character encoding to use
        :type encoding: str
        """

        formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)-8s %(message)s", 
            datefmt="%Y-%m-%d %H:%M:%S")

        handler = logging.FileHandler(path, encoding=encoding, mode="a")

        handler.setLevel("DEBUG")
        handler.setFormatter(formatter)

        Logger.case = logging.getLogger(name)

        Logger.case.addHandler(handler)
        Logger.case.setLevel("DEBUG")

    @staticmethod
    def _set_console_state(state):
        """
        .. py:function:: _set_console_state(state)

        Enables or disables the console stream.

        :param state: boolean representing the future state of the console stream
        :type state: bool
        """

        Logger.console.disabled = not state

    @staticmethod
    def set_console_level(level):
        """
        .. py:function:: set_console_level(level)

        Sets the console logging level.

        :param level: name of the level to set the logging policy to
        :type level: str
        """

        Logger._set_console_state(False) if level == "SUPPRESS" else Logger.console.setLevel(getattr(logging, level))

    @staticmethod
    @_synchronize
    def debug(message):
        """
        .. py:function:: debug(message)

        Prints a debug message.

        :param message: data to print
        :type message: str
        """

        for logger in [
            "case" if hasattr(Logger, "case") else None, 
            "core", 
            "console"]:

            if logger:
                getattr(Logger, logger).debug(message)

    @staticmethod
    @_synchronize
    def info(message):
        """
        .. py:function:: info(message)

        Prints an information message.

        :param message: data to print
        :type message: str
        """

        for logger in [
            "case" if hasattr(Logger, "case") else None, 
            "core", 
            "console"]:

            if logger:
                getattr(Logger, logger).info(message)

    @staticmethod
    @_synchronize
    def warning(message):
        """
        .. py:function:: warning(message)

        Prints a warning message.

        :param message: data to print
        :type message: str
        """

        for logger in [
            "case" if hasattr(Logger, "case") else None, 
            "core", 
            "console"]:

            if logger:
                getattr(Logger, logger).warning(message)

    @staticmethod
    @_synchronize
    def error(message):
        """
        .. py:function:: error(message)

        Prints an error message.

        :param message: data to print
        :type message: str
        """

        for logger in [
            "case" if hasattr(Logger, "case") else None, 
            "core", 
            "console"]:

            if logger:
                getattr(Logger, logger).error(message)

    @staticmethod
    @_synchronize
    def critical(message):
        """
        .. py:function:: critical(message)

        Prints a critical error message.

        :param message: data to print
        :type message: str
        """

        for logger in [
            "case" if hasattr(Logger, "case") else None, 
            "core", 
            "console"]:

            if logger:
                getattr(Logger, logger).critical(message)

    @staticmethod
    @_synchronize
    def exception(message):
        """
        .. py:function:: exception(message)

        Prints the last exception traceback along with an error message.

        :param message: data to print
        :type message: str
        """

        for logger in [
            "case" if hasattr(Logger, "case") else None, 
            "core", 
            "console"]:

            if logger:
                getattr(Logger, logger).exception(message)

    @staticmethod
    @_synchronize
    def inner_exception(message):
        """
        .. py:function:: inner_exception(message)

        Prints the last exception traceback along with an error message.

        :param message: data to print
        :type message: str
        """

        for logger in [
            "case" if hasattr(Logger, "case") else None, 
            "core", 
            "console"]:

            if logger:
                getattr(Logger, logger).exception("InnerException: {}".format(message))

    @staticmethod
    def fault(message, post_mortem=False):
        """
        .. py:function:: fault(message, post_mortem=False)

        Prints the last exception traceback along with an error message then exits the program.

        :param message: data to print
        :type message: str

        :param post_mortem: enable traceback of the last exception raised
        :type post_mortem: bool
        """

        Logger._set_console_state(True)
        Logger.critical(message) if not post_mortem else Logger.exception(message)

        sys.exit(1)
