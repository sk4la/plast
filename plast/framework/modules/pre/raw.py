# -*- coding: utf-8 -*-

from framework.contexts import models as _models

__all__ = [
    "Pre"
]

class Pre(_models.Pre):
    __author__ = "sk4la"
    __description__ = "Feeds raw file(s) to the engine."
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

        self.case.track_files(self.feed)
