# -*- coding: utf-8 -*-

from framework.contexts import models as _models
from framework.contexts.configuration import Configuration as _conf
from framework.contexts.logger import Logger as _log

import multiprocessing
import zipfile

__all__ = [
    "Pre"
]

class Pre(_models.Pre):
    __author__ = "sk4la"
    __description__ = "Unpacks .zip archive(s) and feeds the resulting evidence(s) to the engine."
    __license__ = "GNU GPLv3 <https://github.com/sk4la/plast/blob/master/LICENSE>"
    __maintainer__ = ["sk4la"]
    __system__ = ["Darwin", "Linux", "Windows"]
    __version__ = "0.1"
    __associations__ = {
        "extensions": [
            "zip"
        ],
        "mime": [
            "multipart/x-zip",
            "application/zip",
            "application/zip-compressed",
            "application/x-zip-compressed"
        ]
    }

    def __init__(self, parser):
        parser.add_argument(
            "--level", type=int, choices=range(1, 101), default=10, metavar="NUMBER",
            help="maximum number of level(s) to unpack [10]")

        parser.add_argument(
            "--exclude", nargs="+", metavar="FILTER", 
            help="ignore file(s) matching wildcard filter(s)")

        parser.add_argument(
            "--include", nargs="+", default=_conf.DEFAULTS["INCLUDE_FILTER"], metavar="FILTER", 
            help="only add file(s) matching wildcard filter(s) {}".format(_conf.DEFAULTS["INCLUDE_FILTER"]))

        parser.add_argument(
            "--processes", type=int, choices=range(1, 1001), default=(multiprocessing.cpu_count() or _conf.DEFAULTS["PROCESSES_FALLBACK"]), metavar="NUMBER",
            help="override the number of concurrent processe(s) [{}]".format(multiprocessing.cpu_count() or (_conf.DEFAULTS["PROCESSES_FALLBACK"] if _conf.DEFAULTS["PROCESSES_FALLBACK"] in range(1, 1001) else 4)))

        parser.add_argument(
            "-r", "--recursive", action="store_true", 
            help="unpack archive(s) and walk through directory(ies) recursively")

    # to be multiprocessed
    def _unpack_archive(self, archive, output):
        _log.debug("Unpacking archive <{}>.".format(item))

        with zipfile.ZipFile(archive, "rb") as zipper:
            zipper.extractall(output)

    def run(self):
        """
        .. py:function:: run(self)

        Main entry point for the module.

        :param self: current class instance
        :type self: class
        """

        print("unzipping")
        # tmp = self.case.require_temporary_directory()

        # for item in self.feed:
        #     if os.path.isfile(item):
        #         self._unpack_archive(item, tmp)

        # _log.debug("Tracking file <{}> to <{}>.".format(file, tmp))
