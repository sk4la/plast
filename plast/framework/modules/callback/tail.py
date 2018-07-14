# -*- coding: utf-8 -*-

from framework.api.internal.renderer import Renderer as _renderer

from framework.contexts import models as _models

from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer
import sys

__all__ = [
    "Callback"
]

class Callback(_models.Callback):
    __author__ = "sk4la"
    __description__ = "Simple callback tailing and beautifying match(es)."
    __license__ = "GNU GPLv3 <https://github.com/sk4la/plast/blob/master/LICENSE>"
    __maintainer__ = ["sk4la"]
    __system__ = ["Darwin", "Linux", "Windows"]
    __version__ = "0.1"

    def run(self, data):
        sys.stdout.write(highlight(_renderer.to_json(data, indent=4), JsonLexer(), TerminalFormatter()))
