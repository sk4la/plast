# -*- coding: utf-8 -*-

from framework.api.external import filesystem as _fs
from framework.api.internal import interaction as _interaction

from framework.contexts import models as _models
from framework.contexts.configuration import Configuration as _conf
from framework.contexts.logger import Logger as _log

import os.path
import sys
import zipfile

__all__ = [
    "Pre"
]

class Pre(_models.Pre):
    __author__ = "sk4la"
    __description__ = "Inflates .zip archive(s) and feeds the resulting evidence(s) to the engine."
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
            "--level", type=int, choices=range(101), default=10, metavar="NUMBER", dest="_level", 
            help="maximum number of level(s) to unpack [10]")

        parser.add_argument(
            "--include", nargs="+", default=_conf.DEFAULTS["INCLUSION_FILTERS"], metavar="FILTER", dest="_include", 
            help="only add file(s) matching wildcard filter(s) {}".format(_conf.DEFAULTS["INCLUSION_FILTERS"]))

        parser.add_argument(
            "--exclude", nargs="+", default=_conf.DEFAULTS["EXCLUSION_FILTERS"], metavar="FILTER", dest="_exclude", 
            help="override include and ignore file(s) matching wildcard filter(s)".format(_conf.DEFAULTS["EXCLUSION_FILTERS"]))

        parser.add_argument(
            "--inline-password", metavar="PASSWORD", dest="_inline_password", 
            help="specify an inline password to open the archive(s)")

        parser.add_argument(
            "--password", action="store_true", dest="_password", 
            help="ask for a password to open the archive(s)")

        parser.add_argument(
            "--no-recursion", action="store_true", dest="_no_recursion", 
            help="do not unpack archive(s) and walk through directory(ies) recursively")

    def recursive_inflate(self, archive, output_directory, level=0, password=None):
        if level > self.case.arguments._level:
            _log.warning("Limit unpacking level <{}> exceeded. Stopped unpacking.".format(self.case.arguments._level))
            return

        _log.debug("Inflating {}archive <{}> to temporary directory <{}>.".format("level {} sub".format(level) if level else "base ", archive, output_directory))

        sub_directory = os.path.join(output_directory, os.path.basename(archive))

        try:
            with zipfile.ZipFile(archive) as z:
                z.extractall(path=sub_directory, pwd=(password.encode() if password else password))

        except zipfile.BadZipFile:
            _log.error("Bad file header. Cannot inflate evidence <{}>. Try to filter out non-zip file(s) using --include \"*.zip\" \".*.zip\".".format(archive))
            return

        except RuntimeError as exc:
            if "password required" in str(exc):
                _log.error("Archive <{}> seems to be encrypted. Please specify a password using --password or --inline-password.".format(archive))

            elif "Bad password" in str(exc):
                _log.error("Password {}seems to be incorrect for archive <{}>. Please specify another password using --password or --inline-password.".format("<{}> ".format(self.case.arguments._inline_password) if not hasattr(self, "_password") else "", archive))

            else:
                _log.exception("Runtime exception raised while unpacking archive <{}>.".format(archive))

            return

        except KeyboardInterrupt:
            sys.stderr.write("\n")
            _log.fault("Aborted due to manual user interruption.")

        except Exception:
            _log.exception("Exception raised while unpacking archive <{}>.".format(archive))

        if self.case.arguments._no_recursion:
            return

        for subarchive in _fs.enumerate_matching_files(sub_directory, 
            wildcard_patterns=(["*.{}".format(_) for _ in self.__associations__["extensions"]] + [".*.{}".format(_) for _ in self.__associations__["extensions"]] if hasattr(self, "__associations__") and "extensions" in self.__associations__ else None), 
            mime_types=(self.__associations__["mime"] if hasattr(self, "__associations__") and "mime" in self.__associations__ else None), 
            recursive=True):

            self.recursive_inflate(subarchive, sub_directory, level=(level + 1), password=password)

    def run(self):
        """
        .. py:function:: run(self)

        Main entry point for the module.

        :param self: current class instance
        :type self: class
        """

        if self.case.arguments._inline_password:
            _log.debug("Using inline password <{}> to unpack archive(s).".format(self.case.arguments._inline_password))

        elif self.case.arguments._password:
            self._password = _interaction.password_prompt("Unpacking password: ")

        if self.case.arguments._no_recursion:
            _log.debug("Recursive unpacking manually disabled using --no-recursion.")

        tmp = self.case.require_temporary_directory()

        for evidence in self.feed:
            self.recursive_inflate(evidence, tmp, password=(self.case.arguments._inline_password if not hasattr(self, "_password") else self._password))

        for evidence in _fs.expand_files([tmp],
            recursive=True, 
            include=self.case.arguments._include, 
            exclude=self.case.arguments._exclude):

            print("found {}".format(evidence))
