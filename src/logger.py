import os
import logging

from gunicorn.glogging import Logger


GUNICORN_LOG_PATH = os.environ.get("GUNICORN_LOG_PATH", "logs/gunicorn-daily-log")
DEFAULT_FORMATTER = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] [%(process)d]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S %z")


class MyLogger(Logger):
    """Append an additional time-rotating file logger for Gunicorn."""
    def __init__(self, cfg):
        super().__init__(cfg)
        if len(self.access_log.handlers) > 0:
            out_filename = self.access_log.handlers[0].baseFilename
            tlog = _get_time_file_handler(out_filename, DEFAULT_FORMATTER)
            self.access_log.addHandler(tlog)

        err_tlog = _get_time_file_handler(GUNICORN_LOG_PATH, DEFAULT_FORMATTER)
        self.error_log.addHandler(err_tlog)


def _get_time_file_handler(out_filename, formatter, when="D"):
    tlog = logging.handlers.TimedRotatingFileHandler(filename=out_filename, when=when)
    tlog.setFormatter(formatter)
    return tlog


def get_logger(name):
    logger = logging.getLogger(name)
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt="%(asctime)s %(message)s  [at %(filename)s:%(lineno)d]", datefmt=date_format)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    if len(logger.handlers) > 0:
        rm_idx = [idx for idx, handler in enumerate(logger.handlers) if isinstance(handler, logging.StreamHandler)]
        for idx in rm_idx:
            del logger.handlers[idx]
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
