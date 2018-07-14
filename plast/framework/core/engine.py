# -*- coding: utf-8 -*-

from framework.api.internal import magic as _magic
from framework.api.internal.loader import Loader as _loader

from framework.contexts import models as _models
from framework.contexts.logger import Logger as _log
from framework.contexts.configuration import Configuration as _conf
from framework.contexts.types import Codes as _codes

from framework.core import reader as _reader
from framework.core import processors as _processors

import ctypes
import io
import multiprocessing
import os.path

try:
    import yara

except ImportError as exc:
    _log.fault("Missing dependency <{0}>. Try <pip install {0}> or manually build the required module to fix the issue.".format(exc.name))

__all__ = [
    "Engine"
]

class Engine:
    """Dispatches the processing to asynchronous jobs."""

    def __init__(self, case):
        """
        .. py:function:: __init__(self, case)

        Initialization method for the class.

        :param self: current class instance
        :type self: class

        :param case: filled :code:`contexts.Case` instance
        :type case: class
        """

        self.case = case
        self.buffers = {}

    def _compile_ruleset(self, name, ruleset):
        """
        .. py:function:: _compile_ruleset(self, name, ruleset)

        Compiles and saves YARA rule(s) to the dictionary to be passed to the asynchronous job(s).

        :param self: current class instance
        :type self: class

        :param name: name of the ruleset file to compile the rule(s) from
        :type name: str

        :param ruleset: absolute path to the ruleset file to compile the rule(s) from
        :type ruleset: str

        :return: tuple containing the final status of the compilation and the number of successfully loaded rule(s)
        :rtype: bool, int
        """

        count = 0

        try:
            buffer = io.BytesIO()

            rules = yara.compile(ruleset, includes=_conf.YARA_INCLUDES, error_on_warning=(not self.case.arguments.ignore_warnings))
            rules.save(file=buffer)

            self.buffers[ruleset] = buffer
            count += sum(1 for _ in rules)

            _log.debug("Precompilated YARA ruleset <{}> in memory with a total of <{}> valid rule(s).".format(name, count))
            return (True, count)

        except yara.SyntaxError:
            _log.exception("Syntax error in YARA ruleset <{}>.".format(ruleset))

        except (
            Exception,
            yara.Error):

            _log.exception("Failed to pre-compile ruleset <{}>.".format(ruleset))

        return (False, count)

    def _dispatch_jobs(self):
        """
        .. py:function:: _dispatch_jobs(self)

        Dispatches the processing task(s) to the subprocess(es).

        :param self: current class instance
        :type self: class

        :return: number of match(es)
        :rtype: int
        """

        with multiprocessing.Manager() as manager:
            queue = manager.Queue()
            results = (multiprocessing.Lock(), multiprocessing.Value(ctypes.c_int, 0), manager.list())

            reader = multiprocessing.Process(target=_reader.Reader(queue, results, {
                "target": self.case.resources["matches"],
                "storage": self.case.resources["storage"],
                "format": self.case.arguments.format
            }).run)

            reader.daemon = True
            reader.start()

            _log.debug("Started reader subprocess to consume queue result(s).")

            with _magic.Pool(processes=self.case.arguments.processes) as pool:
                for file in self.case.resources["evidences"]:
                    if os.path.getsize(file) > self.case.arguments.max_size:
                        _log.warning("Evidence <{}> exceeds the maximum size. Ignoring evidence. Try changing --max-size to override this behavior.".format(file))
                        continue

                    pool.starmap_async(
                        _processors.File(self.case.arguments.hash_algorithms, self.case.arguments.callbacks, queue, self.case.arguments.fast).run, 
                        [(file, self.buffers)], 
                        error_callback=_log.inner_exception)

                    _log.debug("Mapped concurrent job to consume evidence <{}>.".format(file))

            queue.put(_codes.DONE)

            with _magic.Hole(KeyboardInterrupt, action=lambda:_log.fault("Aborted due to manual user interruption <SIGINT>.")):
                reader.join()

            return results[1].value

    def _invoke_post_modules(self):
        """
        .. py:function:: _invoke_post_modules(self)

        Invoke the selected :code:`models.Post` module(s).

        :param self: current class instance
        :type self: class
        """

        for name in self.case.arguments.post:
            Module = _loader.load_module(name, _models.Post)

            if Module:
                module = Module()
                module.__name__ = name

                with _magic.Invocator(module):
                    module.run(self.case)

    def run(self):
        """
        .. py:function:: run(self)

        Main entry point for the class.

        :param self: current class instance
        :type self: class
        """

        loaded = {
            "rulesets": 0,
            "rules": 0
        }

        for name, ruleset in _loader.iterate_rulesets():
            status, count = self._compile_ruleset(name, ruleset)

            if status:
                loaded["rulesets"] += 1
                loaded["rules"] += count

        if not loaded["rulesets"]:
            _log.fault("No YARA ruleset(s) loaded. Quitting.")

        _log.info("Applying a total of <{}> YARA rule(s) from <{}> ruleset(s).".format(loaded["rules"], loaded["rulesets"]))
        del loaded

        if not self._dispatch_jobs():
            _log.warning("Skipping <{}> module(s) invocation.".format(_models.Post.__name__))
            return

        self._invoke_post_modules()
