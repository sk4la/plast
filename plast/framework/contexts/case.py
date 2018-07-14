# -*- coding: utf-8 -*-

from framework.api.external import filesystem as _fs
from framework.api.internal import interaction as _interaction

from framework.contexts.logger import Logger as _log
from framework.contexts.configuration import Configuration as _conf

import os
import random
import shutil
import string

try:
    import send2trash

except ImportError as exc:
    _log.fault("Missing dependency <{0}>. Try <pip install {0}> or manually build the required module to fix the issue.".format(exc.name))

__all__ = [
    "Case"
]

class Case:
    """Centralizes the current case's data."""

    def __init__(self, arguments):
        """
        .. py:function:: __init__(self, arguments)

        Initialization method for the class.

        :param self: current class instance
        :type self: class

        :param arguments: :code:`argparse.Parser` instance containing the processed command-line arguments
        :type arguments: list
        """

        self.arguments = arguments
        self.name = os.path.basename(self.arguments.output)

        self.resources = {
            "case": self.arguments.output,
            "matches": os.path.join(self.arguments.output, "{}.{}".format(_conf.MATCHES_FILE_BASENAME, self.arguments.format.lower())),
            "storage": os.path.join(self.arguments.output, _conf.STORAGE_DIRECTORY),
            "evidences": [],
            "temporary": []
        }

        _log.debug("Initialized new case <{}> anchored to <{}>.".format(self.name, self.resources["case"]))

    def __del__(self):
        """
        .. py:function:: __del__(self)

        Destruction method that calls the teardown function(s).

        :param self: current class instance
        :type self: class
        """

        if _conf.KEEP_TEMPORARY_ARTIFACTS:
            _log.warning("Skipped temporary artifact(s) cleanup.")
            return

        self._tear_down()

    def _tear_down(self):
        """
        .. py:function:: _tear_down(self)

        Cleanup method called on class destruction that gets rid of the temporary artifact(s).

        :param self: current class instance
        :type self: class
        """

        for artifact in self.resources["temporary"]:
            try:
                shutil.rmtree(artifact)
                _log.debug("Removed temporary artifact <{}>.".format(artifact))

            except FileNotFoundError:
                _log.debug("Temporary artifact not found <{}>.".format(artifact))

            except (
                OSError,
                Exception):

                _log.exception("Failed to remove temporary artifact <{}>.".format(artifact))

    def _generate_nonce(self, rounds=16):
        """
        .. py:function:: _generate_nonce(self, rounds=16)

        Generates a random string.

        :param self: current class instance
        :type self: class

        :param rounds: number of characters to generate
        :type rounds: int

        :return: random string of :code:`rounds` character(s)
        :rtype: str
        """

        return "".join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(rounds))

    def _create_arborescence(self):
        """
        .. py:function:: _create_arborescence(self)

        Creates the base arborescence for the current case.

        :param self: current class instance
        :type self: class
        """

        if os.path.exists(self.resources["case"]):
            if not self.arguments.overwrite:
                if not _interaction.prompt("Overwrite existing object <{}>?".format(self.resources["case"])):
                    _log.fault("Aborted due to manual user interruption.")

            try:
                send2trash.send2trash(self.resources["case"])
                _log.warning("Overwritten existing object <{}>.".format(self.resources["case"]))

            except (
                send2trash.TrashPermissionError,
                OSError,
                Exception):

                _log.fault("Failed to overwrite existing object <{}>.".format(self.resources["case"]), post_mortem=True)

        _fs.create_local_directory(self.resources["case"])

    def require_temporary_directory(self, seed=None):
        """
        .. py:function:: require_temporary_directory(self, seed=None)

        Creates a temporary directory in the case directory that will be deleted after processing is over.

        :param self: current class instance
        :type self: class

        :param seed: random string
        :type seed: str

        :return: absolute path to the newly created temporary directory
        :rtype: str
        """

        if not seed:
            seed = self._generate_nonce()

        while os.path.isdir(os.path.join(self.resources["case"], seed)):
            seed = self._generate_nonce()

        directory = os.path.join(self.resources["case"], seed)

        _fs.create_local_directory(directory)
        self.resources["temporary"].append(directory)

        return directory

    def _iterate_existing_files(self, evidences):
        """
        .. py:function:: _iterate_existing_files(self, evidences)

        Iterates over file(s) and yields the corresponding path if existing.

        :param self: current class instance
        :type self: class

        :param files: list of file(s) path(s)
        :type files: list

        :return: path to the existing file(s)
        :rtype: str
        """

        for file in evidences:
            if not os.path.isfile(file):
                _log.error("File not found <{}>.".format(file))
                continue

            yield file

    def track_file(self, evidence):
        """
        .. py:function:: track_file(self, evidence)

        Checks and registers an evidence file for processing.

        :param self: current class instance
        :type self: class

        :param evidence: absolute path to the evidence file
        :type evidence: str
        """

        evidence = os.path.abspath(evidence)

        if os.path.isfile(evidence):
            self.resources["evidences"].append(evidence)

        else:
            _log.warning("Evidence <{}> not found or invalid.".format(evidence))

    def track_files(self, evidences, include=[], exclude=[]):
        """
        .. py:function:: track_files(self, evidences)

        Checks and registers multiple evidence files for processing.

        :param self: current class instance
        :type self: class

        :param evidences: list of absolute path(s) to the evidence file(s)
        :type evidences: list

        :param include: list of wildcard pattern(s) to include
        :type include: list

        :param exclude: list of wildcard pattern(s) to exclude
        :type exclude: list
        """

        evidences = [os.path.abspath(evidence) for evidence in evidences]

        for evidence in self._iterate_existing_files(evidences):
            if include and not _fs.matches_patterns(os.path.basename(evidence), patterns=include):
                _log.debug("Ignoring evidence <{}> not matching inclusion pattern(s) <{}>.".format(evidence, include))
                continue

            if exclude and _fs.matches_patterns(os.path.basename(evidence), patterns=exclude):
                _log.debug("Ignoring evidence <{}> matching exclusion pattern(s) <{}>.".format(evidence, exclude))
                continue

            self.track_file(evidence)
