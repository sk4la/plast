# -*- coding: utf-8 -*-

from framework.contexts import errors as _errors
from framework.contexts.configuration import Configuration as _conf
from framework.contexts.meta import Meta as _meta
from framework.contexts.logger import Logger as _log

import fnmatch

try:
    import magic

except ImportError as exc:
    _log.fault("Missing dependency <{0}>. Try <pip install {0}> or manually build the required module to fix the issue.".format(exc.name))

__all__ = [
    "Checker"
]

class Identifier:
    """File identifying class."""

    @staticmethod
    def _iterate_signatures(directory=os.path.join(_meta.__root__, "framework", "signatures"), wildcard_patterns=_conf.YARA_EXTENSION_FILTERS):
        for file in _fs.enumerate_matching_files(directory, wildcard_patterns=wildcard_patterns, recursive=True):
            yield os.path.splitext(os.path.basename(file))[0], file

    @staticmethod
    def _matches_yara_signatures(evidence):
        for ruleset in Identifier._iterate_signatures():
            try:
                rules = yara.compile(ruleset, includes=True, error_on_warning=True)

            except yara.SyntaxError:
                _log.exception("Syntax error in YARA ruleset <{}>.".format(ruleset))

    @staticmethod
    def _matches_mime_types(self, evidence, types=[]):
        """
        .. py:function:: _matches_mime_types(self, evidence, types=[])

        Tests wether a given file matches one or more MIME type(s).

        :param evidence: name of the file to test
        :type evidence: str

        :param types: list of MIME types rendered as strings
        :type types: list

        :return: True if the file matches one or more of the given MIME type(s), else False
        :rtype: bool
        """

        mime = magic.Magic(mime=True)

        if mime.from_file(file) in types:
            return True

        return False

    @staticmethod
    def _matches_patterns(evidence, wildcard_patterns=[]):
        """
        .. py:function:: _matches_patterns(evidence, wildcard_patterns=[])

        Tests whether a given file matches one or more wildcard pattern(s).

        :param evidence: name of the file to test
        :type evidence: str

        :param wildcard_patterns: list of wildcard patterns as strings
        :type wildcard_patterns: list

        :return: True if the file matches one or more of the given patterns, else False
        :rtype: bool
        """

        return any(fnmatch.fnmatch(file, pattern) for pattern in wildcard_patterns)

    @staticmethod
    def _matches_extensions(evidence, extensions=[]):
        """
        .. py:function:: _matches_extensions(evidence, extensions=[])

        Tests whether a given file matches one or more extension(s).

        :param evidence: name of the file to test
        :type evidence: str

        :param extensions: list of file extension(s)
        :type extensions: list

        :return: True if the file matches one or more of the given patterns, else False
        :rtype: bool
        """

        return any(evidence.lower().endswith(".{}".format(extension)) for extension in extensions)

    @staticmethod
    def identify_evidence(self, evidence):
        signature = self.

        if not signature:
            mime = self.get_mime_type(evidence)

            if not mime:
                raise _errors.UnknownType

        return
