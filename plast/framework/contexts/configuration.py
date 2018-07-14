# -*- coding: utf-8 -*-

from framework.api.internal.renderer import Renderer as _renderer

__all__ = [
    "Configuration",
]

class Configuration:
    """Container for the global configuration."""

    @staticmethod
    def _load_configuration(configuration):
        with open(configuration) as conf:
            for key, value in _renderer.from_json(conf.read()).items():
                setattr(Configuration, key, value)
