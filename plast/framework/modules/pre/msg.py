# -*- coding: utf-8 -*-

from framework.contexts import models as _models
from framework.contexts.logger import Logger as _log

try:
    import ExtractMsg

except ImportError as exc:
    _log.fault("Missing dependency <{0}>. Try <pip install https://github.com/mattgwwalker/msg-extractor/zipball/master> or manually build the required module to fix the issue.".format(exc.name))

__all__ = [
    "Pre"
]

class Pre(_models.Pre):
    __author__ = "sk4la"
    __description__ = "Parses .msg file(s), extracts attachment(s) and feeds the resulting evidence(s) to the engine."
    __license__ = "GNU GPLv3 <https://github.com/sk4la/plast/blob/master/LICENSE>"
    __maintainer__ = ["sk4la"]
    __system__ = ["Darwin", "Linux", "Windows"]
    __version__ = "0.1"
    __associations__ = {}

    def run(self):
        """
        .. py:function:: run(self)

        Main entry point for the module.

        :param self: current class instance
        :type self: class
        """

        for evidence in self.feed:
            msg = ExtractMsg.Message(evidence)

            for attachment in msg.attachments:
                print(attachment.shortFilename)

            print("Sender: {}".format(msg.sender))
            print("Sent On: {}".format(msg.date))
            print("Subject: {}".format(msg.subject))
            print("Body: {}".format(msg.body))
