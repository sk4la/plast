#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from framework.contexts.configuration import Configuration as _conf
from framework.contexts.meta import Meta as _meta

_meta.set_package(__file__)
_conf._load_configuration(_meta.__conf__)

from framework.api.external import filesystem as _fs
from framework.api.internal import interaction as _interaction
from framework.api.internal import magic as _magic
from framework.api.internal import parser as _parser
from framework.api.internal.checker import Checker as _checker
from framework.api.internal.loader import Loader as _loader

from framework.contexts import case as _case
from framework.contexts import errors as _errors
from framework.contexts import models as _models
from framework.contexts.logger import Logger as _log

from framework.core import engine as _engine

import framework.modules.callback as _callback
import framework.modules.pre as _pre
import framework.modules.post as _post

import argparse
import multiprocessing
import os.path

__all__ = [
    "main"
]

def _find_association(modules, meta):
    """
    .. py:function:: _find_association(modules, meta)

    Finds association(s) to :code:`meta` in the available preprocessing module(s).

    :param modules: dictionary containing the loaded module(s)
    :type modules: dictionary

    :param meta: object containing metadata for the target file
    :type meta: class

    :return: tuple containing the name of the associated module and actual module object
    :rtype: tuple

    :raises UnsupportedType: if :code:`meta` cannot be handled by the available preprocessing module(s)
    """

    for name, Module in modules.items():
        if hasattr(Module, "__associations__") and (meta.mime in Module.__associations__.get("mime", []) or meta.extension in Module.__associations__.get("extensions", [])):
            return name, Module

    raise _errors.UnsupportedType

def _dispatch_preprocessing(modules, case, feed):
    """
    .. py:function:: _dispatch_preprocessing(container, case, feed)

    Guessing function that dispatches preprocessing using MIME-types.

    :param modules: dictionary containing the loaded module(s)
    :type modules: dictionary

    :param case: preloaded Case class
    :type case: class

    :param feed: flattened list of evidence(s)
    :type feed: list
    """

    tasks = {}

    for file in feed:
        meta = _fs.guess_file_type(file)

        if not meta:
            tasks.setdefault(("raw", modules["raw"]), []).append(file)
            _log.warning("Could not determine data type. Added evidence <{}> to the force-feeding list.".format(file))
            continue

        try:
            name, Module = _find_association(modules, meta)

            tasks.setdefault((name, Module), []).append(file)
            _log.debug("Identified data type <{}> for evidence <{}>. Dispatching to <{}>.".format(meta.mime, file, name))

        except _errors.UnsupportedType:
            tasks.setdefault(("raw", modules["raw"]), []).append(file)
            _log.warning("Data type <{}> unsupported. Added evidence <{}> to the force-feeding list.".format(meta.mime, file))

    if tasks:
        for (name, Module), partial_feed in tasks.items():
            if _interaction.prompt("Found <{}> evidence(s) that can be dispatched. Do you want to automatically invoke the <{}> module using default option(s)?".format(len(partial_feed), name), default_state=True):
                Module.case = case
                Module.feed = partial_feed

                with _magic.Hole(Exception, action=lambda:_log.fault("Fatal exception raised within preprocessing module <{}>.".format(name), post_mortem=True)), _magic.Invocator(Module):
                    Module.run()

                del Module

def _argparser(parser):
    """
    .. py:function:: _argparser(parser)

    Command-line argument parsing function.

    :param parser: :code:`argparse.Parser` instance
    :type parser: class

    :param parser: tuple containing the loaded module(s) and the processed command-line argument(s)
    :rtype: tuple
    """

    modules = {}

    parser.add_argument(
        "-i", "--input", nargs="+", action=_parser.AbsolutePathMultiple, required=True, metavar="PATH", 
        help="input file(s) or directory(ies)")

    parser.add_argument(
        "-o", "--output", required=True, action=_parser.AbsolutePath, metavar="PATH",
        help="path to the output directory to be created for the current case")

    parser.add_argument(
        "--callbacks", nargs="*", choices=_loader.render_modules(_callback, _models.Callback), default=(_loader.render_modules(_callback, _models.Callback) if _conf.INVOKE_ALL_MODULES_IF_NONE_SPECIFIED else []), action=_parser.Unique,
        help="select the callback(s) that will handle the resulting data [*]")

    parser.add_argument(
        "--exclude", nargs="+", default=_conf.DEFAULTS["EXCLUSION_FILTERS"], metavar="FILTER", 
        help="override include and ignore file(s) matching wildcard filter(s) {}".format(_conf.DEFAULTS["EXCLUSION_FILTERS"]))

    parser.add_argument(
        "--fast", action="store_true", default=_conf.DEFAULTS["YARA_FAST_MODE"],
        help="enable YARA's fast matching mode")

    parser.add_argument(
        "--format", choices=["json"], default=_conf.DEFAULTS["OUTPUT_FORMAT"].lower(),
        help="output format for detection(s) {}".format(_conf.DEFAULTS["OUTPUT_FORMAT"].lower()))

    parser.add_argument(
        "--hash-algorithms", nargs="+", action=_parser.Unique, metavar="NAME",
        choices=["md5", "sha1", "sha224", "sha256", "sha384", "sha512", "blake2b", "blake2s", "sha3_224", "sha3_256", "sha3_384", "sha3_512"], default=[item.lower() for item in _conf.DEFAULTS["HASH_ALGORITHMS"]], 
        help="output format for detection(s), see hashlib API reference for supported algorithm(s) {}".format([item.lower() for item in _conf.DEFAULTS["HASH_ALGORITHMS"]]))

    parser.add_argument(
        "--ignore-warnings", action="store_true", default=_conf.YARA_ERROR_ON_WARNING,
        help="ignore YARA compilation warning(s)")

    parser.add_argument(
        "--include", nargs="+", default=_conf.DEFAULTS["INCLUSION_FILTERS"], metavar="FILTER", 
        help="only add file(s) matching wildcard filter(s) {}".format(_conf.DEFAULTS["INCLUSION_FILTERS"]))

    parser.add_argument(
        "--logging", choices=["debug", "info", "warning", "error", "critical", "suppress"], default=_conf.DEFAULTS["LOGGING_LEVEL"].lower(),
        help="override the default console logging level [{}]".format(_conf.DEFAULTS["LOGGING_LEVEL"].lower()))

    parser.add_argument(
        "--max-size", type=int, default=300000000, metavar="BYTES",
        help="maximum size for the evidence(s) [300MB]")

    parser.add_argument(
        "--no-prompt", action="store_true", default=_conf.DEFAULTS["NO_PROMPT"],
        help="always use default answer when prompted")

    parser.add_argument(
        "--overwrite", action="store_true",
        help="force the overwriting of an existing output directory")

    parser.add_argument(
        "--post", nargs="*", choices=_loader.render_modules(_post, _models.Post), default=(_loader.render_modules(_post, _models.Post) if _conf.INVOKE_ALL_MODULES_IF_NONE_SPECIFIED else []), action=_parser.Unique,
        help="select the postprocessing module(s) that will handle the resulting data [*]")

    parser.add_argument(
        "--processes", type=int, choices=range(1, 1001), default=(multiprocessing.cpu_count() or _conf.DEFAULTS["PROCESSES_FALLBACK"]), metavar="NUMBER",
        help="override the number of concurrent processe(s) [{}]".format(multiprocessing.cpu_count() or (_conf.DEFAULTS["PROCESSES_FALLBACK"] if _conf.DEFAULTS["PROCESSES_FALLBACK"] in range(1, 1001) else 4)))

    parser.add_argument(
        "-r", "--recursive", action="store_true", 
        help="walk through directory(ies) recursively")

    parser.add_argument("-", dest="_dummy", action="store_true", 
        help=argparse.SUPPRESS)

    for name, Module in _loader.iterate_modules(_pre, _models.Pre):
        subparser = parser.subparsers.add_parser(name, description=getattr(Module, "__description__", None), add_help=False)

        modules[name] = Module(subparser)
        modules[name].__name__ = name

        with _magic.Hole(argparse.ArgumentError):
            parser.register_help_hook(subparser)

            if getattr(modules[name], "__version__", None):
                parser.register_version(subparser, modules[name].__name__, modules[name].__version__)

    return modules, parser.parse_args()

def _initialize(container):
    """
    .. py:function:: _initialize(container)

    Local entry point for the program.

    :param container: tuple containing the loaded module(s) and processed command-line argument(s)
    :type container: tuple
    """

    del container[1]._dummy

    modules = container[0]
    args = container[1]

    _log.set_console_level(args.logging.upper())

    if not _checker.number_rulesets():
        _log.fault("No YARA rulesets found. Nothing to be done.")

    if args.no_prompt:
        _conf.DEFAULTS["NO_PROMPT"] = True

    case = _case.Case(args)
    case._create_arborescence()

    if _conf.CASE_WIDE_LOGGING:
        _log._create_file_logger("case", os.path.join(case.resources["case"], "{}.log".format(_meta.__package__)), level=_conf.CASE_WIDE_LOGGING_LEVEL, encoding=_conf.OUTPUT_CHARACTER_ENCODING)

    feed = _fs.expand_files(args.input, 
        recursive=args.recursive, 
        include=args.include, 
        exclude=args.exclude)

    if not feed:
        _log.fault("No evidence(s) to process. Quitting.")

    if args._subparser:
        Module = container[0][args._subparser]
        Module.case = case
        Module.feed = feed

        with _magic.Hole(Exception, action=lambda:_log.fault("Fatal exception raised within preprocessing module <{}>.".format(args._subparser), post_mortem=True)), _magic.Invocator(Module):
            Module.run()

        del Module

    else:
        _log.debug("Guessing data type(s).")
        _dispatch_preprocessing(modules, case, feed)

    if not case.resources["evidences"]:
        _log.fault("No evidence(s) to process. Quitting.")

    _log.info("Currently tracking <{}> evidence(s).".format(len(case.resources["evidences"])))

    if case.arguments.fast:
        _log.warning("Fast mode is enabled. Some strings occurences may be ommited.")

    _engine.Engine(case).run()

def main():
    """
    .. py:function:: main()

    Main entry point for the program.
    """

    try:
        _initialize(_argparser(_parser.Parser()))

    except SystemExit:
        pass

    except:
        _log.fault("Unhandled exception trapped. Quitting.", post_mortem=True)

if __name__ == "__main__":
    main()
