# -*- coding: utf-8 -*-

from framework.contexts.logger import Logger as _log
from framework.contexts.meta import Meta as _meta

import argparse
import os.path

__all__ = [
    "Parser",
    "AbsolutePath",
    "AbsolutePathMultiple",
    "Unique"
]

class Parser:
    """Custom CLI arguments parser."""

    def __init__(self):
        """
        .. py:function:: __init__(self)

        Initialization method for the class.

        :param self: current class instance
        :type self: class
        """

        self.parser = argparse.ArgumentParser(
            prog=_meta.__package__,
            description="This tool must ALWAYS be used in a confined environment.",
            add_help=False)

        self.register_help_hook(self.parser)
        self.register_version(self.parser, _meta.__package__, _meta.__version__)

        self.subparsers = self.parser.add_subparsers(dest="_subparser")

    def register_help_hook(self, parser):
        """
        .. py:function:: register_help_hook(self, parser)

        Adds a help menu in :code:`parser`.

        :param self: current class instance
        :type self: class

        :param parser: :code:`argparse.Parser` or :code:`argparse.Parser.subparser` instance
        :type parser: class
        """

        parser.add_argument(
            "--help", action="help",
            help="display the help menu")

    def register_version(self, parser, name, version):
        """
        .. py:function:: register_version(self, parser, name, version)

        Adds a version option in :code:`parser`.

        :param self: current class instance
        :type self: class

        :param parser: :code:`argparse.Parser` or :code:`argparse.Parser.subparser` instance
        :type parser: class

        :param name: name of the target
        :type name: str

        :param version: version number of the target
        :type version: str
        """

        parser.add_argument(
            "--version", action="version", version="{} {}".format(name, version),
            help="display the version number")

    def print_help(self):
        """
        .. py:function:: print_help(self)

        Trigger the :code:`print_help` method from the current parser.

        :param self: current class instance
        :type self: class
        """

        self.parser.print_help()

    def add_argument(self, *args, **kwargs):
        """
        .. py:function:: add_argument(self, *args, **kwargs)

        Registers a command-line argument in the main parser.

        :param self: current class instance
        :type self: class

        :param *args: list of value(s)
        :type *args: list

        :param **kwargs: dictionary containing key/value association(s)
        :type **kwargs: dict
        """

        self.parser.add_argument(*args, **kwargs)

    def parse_args(self):
        """
        .. py:function:: parse_args(self)

        Triggers the :code:`parse_args` method from the main parser.

        :param self: current class instance
        :type self: class

        :return: :code:`argparse.Parser` instance containing the processed command-line arguments
        :rtype: class
        """

        return self.parser.parse_args()

class AbsolutePath(argparse.Action):
    """Custom :code:`argparse` action that calls the :code:`os.path.abspath` method on the target."""

    def __call__(self, parser, namespace, values, option=None):
        """
        .. py:function:: __call__(self, parser, namespace, values, option=None)

        Callback method called when the action is invoked.

        :param self: current class instance
        :type self: class

        :param parser: :code:`argparse.Parser` or :code:`argparse.Parser.subparser` instance
        :type parser: class

        :param namespace: object that will be returned by the :code:`parse_args` method
        :type namespace: class

        :param values: associated command-line arguments
        :type values: list

        :param option: option string that was used to invoke this action
        :type option: str
        """

        setattr(namespace, self.dest, os.path.abspath(os.path.expanduser(values)))

class AbsolutePathMultiple(argparse._AppendAction):
    """Custom :code:`argparse` action that calls the :code:`os.path.abspath` method on every item."""

    def __call__(self, parser, namespace, values, option=None):
        """
        .. py:function:: __call__(self, parser, namespace, values, option=None)

        Callback method called when the action is invoked.

        :param self: current class instance
        :type self: class

        :param parser: :code:`argparse.Parser` or :code:`argparse.Parser.subparser` instance
        :type parser: class

        :param namespace: object that will be returned by the :code:`parse_args` method
        :type namespace: class

        :param values: associated command-line arguments
        :type values: list

        :param option: option string that was used to invoke this action
        :type option: str
        """

        setattr(namespace, self.dest, [os.path.abspath(os.path.expanduser(item)) for item in values])

class Unique(argparse.Action):
    """Custom :code:`argparse` action that removes duplicate(s)."""

    def __call__(self, parser, namespace, values, option=None):
        """
        .. py:function:: __call__(self, parser, namespace, values, option=None)

        Callback method called when the action is invoked.

        :param self: current class instance
        :type self: class

        :param parser: :code:`argparse.Parser` or :code:`argparse.Parser.subparser` instance
        :type parser: class

        :param namespace: object that will be returned by the :code:`parse_args` method
        :type namespace: class

        :param values: associated command-line arguments
        :type values: list

        :param option: option string that was used to invoke this action
        :type option: str
        """

        setattr(namespace, self.dest, set(values))
