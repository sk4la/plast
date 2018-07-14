#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from framework.contexts.meta import Meta as _meta

import os
import subprocess

__all__ = [
    "main"
]

def main():
    """
    .. py:function:: main()

    Main entry point for the program.
    """

    subprocess.call([os.environ.get("EDITOR", "vim"), _meta.__conf__])

if __name__ == "__main__":
    main()
