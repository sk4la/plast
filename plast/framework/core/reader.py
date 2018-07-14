# -*- coding: utf-8 -*-

from framework.api.external import filesystem as _fs
from framework.api.internal import magic as _magic
from framework.api.internal.renderer import Renderer as _renderer

from framework.contexts.logger import Logger as _log
from framework.contexts.configuration import Configuration as _conf
from framework.contexts.meta import Meta as _meta
from framework.contexts.types import Codes as _codes

import os
import shutil
import stat

__all__ = [
    "Reader"
]

class Reader:
    """Processes the content from the :code:`multiprocessing.Queue` instance."""

    def __init__(self, queue, results, target):
        """
        .. py:function:: __init__(self, queue, results, target)

        Initialization method for the class.

        :param self: current class instance
        :type self: class

        :param queue: :code:`multiprocessing.Manager.Queue` instance
        :type queue: class

        :param results: :code:`multiprocessing.Value` instance
        :type results: class

        :param target: dictionary containing the absolute path to the output file and the data format to use
        :type target: dict
        """

        self.queue = queue
        self.results = results
        self.target = target

        self.map = {
            "json": self._append_json
        }

    def _append_json(self, data):
        """
        .. py:function:: _append_json(self, data)

        Encodes the match data using the given format and appends the match data to the output file.

        :param self: current class instance
        :type self: class

        :param data: dictionary containing the match data
        :type data: dict
        """

        try:
            self.output.write("{}\n".format(_renderer.to_json(data)))

        except _errors.CharacterEncodingError:
            _log.error("Cannot decode data from <{}>.".format(data["target"]["identifier"]))

        except InvalidObject:
            _log.exception("Exception raised while retrieving matching data from <{}>.".format(data["target"]["identifier"]))

    def _open_output_file(self, mode="a", character_encoding=_conf.OUTPUT_CHARACTER_ENCODING):
        """
        .. py:function:: _open_output_file(self, mode="a", character_encoding=conf.OUTPUT_CHARACTER_ENCODING)

        Opens the output stream.

        :param self: current class instance
        :type self: class

        :param mode: file opening mode to use
        :type mode: str
        
        :param character_encoding: character encoding to use
        :type character_encoding: str

        :return: descriptor for the newly opened file stream
        :rtype: class
        """

        try:
            return open(self.target["target"], mode=mode, encoding=character_encoding)

        except (
            OSError,
            Exception):

            _log.fault("Failed to open <{}> for writing.".format(self.target["target"]), post_mortem=True)

    def _read_queue(self):
        """
        .. py:function:: _read_queue(self)

        Main loop that processes the match(es) from the :code:`multiprocessing.Queue` instance.

        :param self: current class instance
        :type self: class
        """

        while True:
            item = self.queue.get()

            if item == _codes.DONE:
                break

            self.map[self.target["format"]](item)

            with self.results[0]:
                self.results[1].value += 1

            self.results[2].append(item["target"]["identifier"])

            _log.debug("Matching signature from rule <{}> on evidence <{}>.".format(item["match"]["rule"], item["target"]["identifier"]))

    def _store_matching_evidences(self):
        """
        .. py:function:: _store_matching_evidences(self)

        Saves the matching evidence(s) to the specified storage directory.

        :param self: current class instance
        :type self: class
        """

        for evidence in self.results[2]:
            if not os.path.isdir(self.target["storage"]):
                _fs.create_local_directory(self.target["storage"])

            try:
                storage_path = (os.path.join(self.target["storage"], os.path.basename(evidence)) if not _conf.NEUTRALIZE_MATCHING_EVIDENCES else os.path.join(self.target["storage"], "{}.{}".format(os.path.basename(evidence), _meta.__package__)))

                shutil.copy2(evidence, storage_path)

                if _conf.NEUTRALIZE_MATCHING_EVIDENCES:
                    os.chmod(storage_path, stat.S_IMODE(os.lstat(storage_path).st_mode) & ~stat.S_IEXEC)

                _log.debug("Saved {}matching evidence <{}> as <{}>.".format("and neutralized " if _conf.NEUTRALIZE_MATCHING_EVIDENCES else "", os.path.basename(evidence), storage_path))

            except (
                OSError,
                shutil.Error,
                Exception):

                _log.exception("Failed to save matching evidence <{}> as <{}>.".format(os.path.basename(evidence), storage_path))

    def run(self):
        """
        .. py:function:: run(self)

        Main entry point for the class.

        :param self: current class instance
        :type self: class
        """

        with self._open_output_file() as self.output:
            self._read_queue()

        with self.results[0], _magic.OverrideConsoleLogging("WARNING"):
            _log.warning("Total of <{}> matching pattern(s). See <{}> for more details.".format(self.results[1].value, self.target["target"])) if self.results[1].value else _log.info("No matching pattern(s) found.")

        self._store_matching_evidences()
