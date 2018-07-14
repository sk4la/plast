# -*- coding: utf-8 -*-

from framework.api.external import rendering as _rendering

from framework.api.internal import magic as _magic
from framework.api.internal.loader import Loader as _loader

from framework.contexts import models as _models
from framework.contexts.configuration import Configuration as _conf
from framework.contexts.logger import Logger as _log
from framework.contexts.meta import Meta as _meta

import hashlib
import os.path

try:
    import pendulum
    import yara

except ImportError as exc:
    _log.fault("Missing dependency <{0}>. Try <pip install {0}> or manually build the required module to fix the issue.".format(exc.name))

__all__ = [
    "File",
    "Process"
]

class File:
    """Core multiprocessed class that processes the evidence(s) asynchronously."""

    def __init__(self, algorithms, callbacks, queue, fast=False):
        """
        .. py:function:: __init__(self, algorithms, callbacks, queue)

        Initialization method for the class.

        :param self: current class instance
        :type self: class

        :param algorithms: list containing the name of the hash algorithm(s) to use
        :type algorithms: list

        :param callbacks: list containing the name of the :code:`models.Callback` modules to invoke
        :type callbacks: list

        :param fast: flag specifying whether YARA must be performing a fast scan
        :type fast: bool

        :param queue: :code:`multiprocessing.Manager.Queue` instance
        :type queue: class
        """

        self.algorithms = algorithms
        self.callbacks = callbacks
        self.queue = queue
        self.fast = fast

    def _compute_hash(self, evidence, algorithm="sha256", buffer_size=65536):
        """
        .. py:function:: _compute_hash(self, evidence, algorithm="sha256", buffer_size=65536)

        Computes the hash from the evidence's data.

        :param self: current class instance
        :type self: class

        :param evidence: absolute path to the evidence to compute the hash from
        :type evidence: str

        :param algorithm: lowercase name of the hash algorithm to compute
        :type algorithm: str

        :param buffer_size: size of the buffer
        :type buffer_size: int

        :return: hexadecimal digest of the given file
        :rtype: str
        """

        with open(evidence, "rb") as file:
            cipher = getattr(hashlib, algorithm)()

            while True:
                data = file.read(buffer_size)

                if not data:
                    break

                cipher.update(data)
                
        return cipher.hexdigest()

    def _invoke_callbacks(self, data):
        """
        .. py:function:: _invoke_callbacks(self, data)

        Invokes the selected :code:`models.Callback` module(s) with the matching data.

        :param self: current class instance
        :type self: class

        :param data: dictionary containing the match data
        :type data: dict
        """

        for name in self.callbacks:
            Module = _loader.load_module(name, _models.Callback)

            if Module:
                module = Module()
                module.__name__ = name

                with _magic.Invocator(module):
                    module.run(data)

    def _consume_evidence(self):
        """
        .. py:function:: _consume_evidence(self)

        Main loop that processes the evidence(s) and formats the match(es).

        :param self: current class instance
        :type self: class
        """

        for _, buffer in self.buffers.items():
            try:
                for match in buffer.match(self.evidence, timeout=_conf.YARA_MATCH_TIMEOUT, fast=self.fast):
                    hashes = {}

                    for algorithm in self.algorithms:
                        hashes[algorithm] = self._compute_hash(self.evidence, algorithm=algorithm)

                    for action in [self.queue.put, self._invoke_callbacks]:
                        action({
                            "origin": _meta.__package__,
                            "target": {
                                "type": "file",
                                "identifier": self.evidence
                            },
                            "match": {
                                "timestamp": _rendering.timestamp(),
                                "rule": match.rule,
                                "meta": match.meta,
                                "namespace": match.namespace,
                                "tags": match.tags,
                                "hashes": hashes,
                                "strings": [{
                                    "offset": string[0],
                                    "reference": string[1], 
                                    "litteral": string[2].decode("utf-8", "backslashreplace")} for string in match.strings]
                            }
                        })

            except yara.TimeoutError:
                _log.warning("Timeout exceeded for evidence <{}>.".format(self.evidence))
                continue

            except (
                yara.Error,
                Exception):

                _log.exception("YARA exception raised during processing of evidence <{}>.".format(self.evidence))
                continue

    def run(self, evidence, buffers):
        """
        .. py:function:: run(self, evidence, buffers)

        Main entry point for the class.

        :param self: current class instance
        :type self: class

        :param evidence: absolute path to the evidence file to consume
        :type evidence: str

        :param buffers: dictionary containing precompiled YARA rule(s)
        :type buffers: dict
        """

        self.evidence = evidence
        self.buffers = buffers

        _loader._load_memory_buffers(self.buffers)
        self._consume_evidence()
