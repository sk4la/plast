# -*- coding: utf-8 -*-

from framework.api.external import filesystem as _fs

from framework.contexts import models as _models
from framework.contexts.configuration import Configuration as _conf
from framework.contexts.logger import Logger as _log

import base64
import multiprocessing
import os.path

try:
    import eml_parser

except ImportError as exc:
    _log.fault("Missing dependency <{0}>. Try <pip install {0}> or manually build the required module to fix the issue. Module <{0}> may require the installation of the <{1}> library.".format(exc.name, "libmagic"))

__all__ = [
    "Pre"
]

class Pre(_models.Pre):
    __author__ = "sk4la"
    __description__ = "Parses .eml file(s), extracts attachment(s) and feeds the resulting evidence(s) to the engine."
    __license__ = "GNU GPLv3 <https://github.com/sk4la/plast/blob/master/LICENSE>"
    __maintainer__ = ["sk4la"]
    __system__ = ["Darwin", "Linux", "Windows"]
    __version__ = "0.1"
    __associations__ = {
        "extensions": [
            "eml"
        ]
    }

    def __init__(self, parser):
        parser.add_argument(
            "--exclude", nargs="+", default=_conf.DEFAULTS["EXCLUSION_FILTERS"], metavar="FILTER", dest="_exclude", 
            help="ignore file(s) matching wildcard filter(s) {}".format(_conf.DEFAULTS["EXCLUSION_FILTERS"]))

        parser.add_argument(
            "--include", nargs="+", default=_conf.DEFAULTS["INCLUSION_FILTERS"], metavar="FILTER", dest="_include", 
            help="only add file(s) matching wildcard filter(s) {}".format(_conf.DEFAULTS["INCLUSION_FILTERS"]))

    def run(self):
        """
        .. py:function:: run(self)

        Main entry point for the module.

        :param self: current class instance
        :type self: class
        """

        tmp = self.case.require_temporary_directory()

        for evidence in self.feed:
            try:
                mail = eml_parser.eml_parser.decode_email(evidence, include_raw_body=True, include_attachment_data=True)
                _log.info("Extracted <{}> attachment(s) from <{}>.".format(len(mail["attachment"]), evidence))

            except Exception:
                _log.exception("Failed to extract data from <{}>. Ignoring evidence.".format(evidence))
                continue

            output_directory = os.path.join(tmp, os.path.basename(evidence))

            if not os.path.isdir(output_directory):
                _fs.create_local_directory(output_directory)

            for attachment in mail["attachment"]:
                if not attachment["filename"]:
                    attachment["filename"] = idx

                if not _fs.matches_patterns(attachment["filename"], self.case.arguments._include):
                    _log.warning("Ignoring attachment <{}> not matching inner inclusion pattern(s).".format(attachment["filename"]))
                    continue

                if _fs.matches_patterns(attachment["filename"], self.case.arguments._exclude):
                    _log.warning("Ignoring attachment <{}> matching inner exclusion pattern(s).".format(attachment["filename"]))
                    continue

                output_path = os.path.join(output_directory, attachment["filename"])

                with open(output_path, "wb") as out:
                    out.write(base64.b64decode(attachment["raw"]))

                _log.debug("Attachment <{}> extracted from <{}> stored locally as <{}>.".format(attachment["filename"], evidence, output_path))

                self.case.track_file(output_path)
