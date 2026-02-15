import logging
import sys


def setup_logger(verbose: bool = False) -> logging.Logger:
    logger = logging.getLogger("indieshout")

    if logger.handlers:
        return logger

    level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)

    fmt = "%(levelname)s: %(message)s"
    if verbose:
        fmt = "%(asctime)s %(levelname)s [%(name)s] %(message)s"

    handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(handler)

    return logger
