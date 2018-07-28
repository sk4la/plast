# -*- coding: utf-8 -*-

from framework.api.internal.checker import Checker as _checker

from framework.contexts import errors as _errors
from framework.contexts.configuration import Configuration as _conf
from framework.contexts.logger import Logger as _log

import getpass
import sys

try:
    from colorama import Fore, Style

except ImportError as exc:
    _log.fault("Missing dependency <{0}>. Try <pip install {0}> or manually build the required module to fix the issue.".format(exc.name))

__all__ = [
    "password_prompt",
    "prompt"
]

def password_prompt(message=None, rounds=_conf.PROMPT_ROUNDS):
    """
    .. py:function:: password_prompt(rounds=_conf.PROMPT_ROUNDS)

    Prompts the user for a password.

    :param message: question to ask
    :type message: str

    :param rounds: number of times to prompt before aborting
    :type rounds: int
    """

    for _ in range(rounds):
        try:
            password = getpass.getpass("{}{}{}{}{}".format(
                Fore.WHITE, 
                Style.BRIGHT, 
                message, 
                Fore.RESET, 
                Style.RESET_ALL)) if message else getpass.getpass()

        except KeyboardInterrupt:
            sys.stderr.write("\n")
            _log.fault("Aborted due to manual user interruption.")

        try:
            if getpass.getpass("{}{}Confirm:{}{}".format(
                Fore.WHITE, 
                Style.BRIGHT, 
                Fore.RESET, 
                Style.RESET_ALL)) == password:

                _log.debug("Unpacking password successfully set.")
                return password

        except KeyboardInterrupt:
            sys.stderr.write("\n")
            _log.fault("Aborted due to manual user interruption.")

    _log.fault("No valid password provided. Aborting.")

def prompt(message, rounds=_conf.PROMPT_ROUNDS, default_state=False):
        """
        .. py:function:: prompt(message, rounds=_conf.PROMPT_ROUNDS, default_state=False)

        Prompts the user with a yes/no question and wait for a valid answer.

        :param message: question to ask
        :type message: str

        :param rounds: number of times to prompt before aborting
        :type rounds: int

        :param default_state: default answer
        :type default_state: bool

        :return: boolean representing the user's answer
        :rtype: bool
        """

        if _conf.DEFAULTS["NO_PROMPT"]:
            _log.debug("Prompt suppressed, using default answer <{}>. Try --no-prompt or conf.NO_PROMPT to change this behavior.".format("yes" if default_state else "no"))
            return default_state

        key_map = {
            "yY": True,
            "nN": False
        }

        for _ in range(rounds):
            try:
                answer = _checker.sanitize_data(input("{}{}{} [{}{}]{}{} ".format(
                    Fore.WHITE, 
                    Style.BRIGHT, 
                    message, 
                    "Y" if default_state else "y", 
                    "N" if not default_state else "n", 
                    Fore.RESET, 
                    Style.RESET_ALL)))

            except _errors.MalformatedData:
                _log.fault("Malformated input.")

            except KeyboardInterrupt:
                sys.stderr.write("\n")
                _log.fault("Aborted due to manual user interruption.")

            if not answer:
                return default_state

            for key, state in key_map.items():
                if answer in key:
                    return state

        _log.warning("No valid answer provided. Using default answer <{}>.".format("yes" if default_state else "no"))
        return default_state
