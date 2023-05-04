import logging.config
import os
import string
from typing import Any
from pathlib import Path
import yaml
import sys
from uvicorn.workers import UvicornWorker
from nice_test.options import pre_main
from functools import partialmethod
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL


class NTUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {
        "log_config": Path(sys.prefix, 'config', 'logging.yaml'),
    }


def load(app_name: str, app_version: str, cfg: Path = None, prefix: dict = None, debug: bool = False):
    """
    Loads logging configuration
    arugments:
        app_name: name of the application
        app_version: version of the application
    keyword arguments:
        cfg: path to logging configuration file
        prefix: prefix for logging
        debug: enable debug output
    """

    prefix = prefix or {}
    prefix_default = {
        'app_name': app_name,
        'app_version': app_version,
        'default_level': 'DEBUG' if debug else 'INFO',
        'pid': str(os.getpid()),
    }
    extra = {**prefix, **prefix_default}

    if not cfg:
        cfg = pre_main(app_name, app_version, _make_parser=None, cfg_default=None)

    _load(cfg=cfg, extra=extra, debug=debug)


def _load(cfg: dict, extra: dict = None, debug: bool = False):
    """
    Loads logging configuration
    arugments:
        cfg: logging configuration
    keyword arguments:
        extra: extra logging context
        debug: enable debug output
    """

    extra = extra or {}
    if debug:
        for handler in cfg.get('handlers', {}):
            cfg['handlers'][handler]['level'] = 'DEBUG'
        cfg['root']['level'] = 'DEBUG'

    cfg.logging.version = 1

    for handler in cfg.logging.handlers:
        if cfg.logging.handlers[handler].get('filename', None):
            cfg.logging.handlers[handler]['filename'] = cfg.prefix + cfg.logging.handlers[handler].filename

    logging.config.dictConfig(cfg.logging)

    logger = NTLog.getLogger(__name__, extra)
    logger.debug('Logging configuration loaded')


class NTLogException(Exception):
    pass


def getLogger(name, extra={}):
    return NTLog.getLogger(name, extra)


class _PartialFormatter(string.Formatter):
    """
    Partial string formatter
    """

    def get_value(self, key, args, kwargs):
        try:
            return super().get_value(key, args, kwargs)
        except KeyError:
            return ''


class _NTStyle(logging.StrFormatStyle):
    """Custom logginng style"""

    formatter = _PartialFormatter()

    def format(self, record):
        return self.formatter.format(self._fmt, **record.__dict__)


class NTFormatter(logging.Formatter):
    default_msec_format = '%s.%03d'

    def __init__(self, fmt=None, datefmt=None, style='{'):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        self._style = _NTStyle(fmt)


class NTLog(logging.LoggerAdapter):
    """
    Adapt logging for NiceTest
    """

    def __init__(self, logger, extra):
        if isinstance(logger, logging.LoggerAdapter):
            self.logger = logging.getLogger(logger)
        else:
            self.logger = logger
        self.extra = extra or {}

    @classmethod
    def getLogger(cls, name: Any, extra: dict = {}):
        return NTLog(logging.getLogger(name), extra)

    def log(self, level, msg, *args, **kwargs):
        """
        Delegate logging to the underlying logger
        after adding additional context.
        """
        if self.isEnabledFor(level):
            extra = {
                **self.extra,
                **(kwargs.get('extra') or {}),
            }
            kwargs['extra'] = extra
            self.logger._log(level, msg, args, **kwargs)

    debug = partialmethod(log, DEBUG)
    info = partialmethod(log, INFO)
    warning = partialmethod(log, WARNING)
    error = partialmethod(log, ERROR)
    exception = partialmethod(log, ERROR, exc_info=True)
    critical = partialmethod(log, CRITICAL)
    fatal = partialmethod(log, CRITICAL)


class NTFilter(logging.Filter):
    fmt = '[{0}={1}]'

    def __init__(self, prefix=None, extra=None):
        super().__init__()
        self.prefix = prefix
        self.extra = extra or {}

    def add_tag(self, key, value):
        self.extra[key] = value

    def filter(self, record):
        for k, v in self.extra.items():
            setattr(record, k, v)

        r = record.__dict__
        record.extra = ' '.join([self.fmt.format(k, r[k]) for k in self.prefix if k in r])

        return True
