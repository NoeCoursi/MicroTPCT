import logging
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
) -> logging.Logger:
    """
    Configure and return a logger.

    Parameters
    ----------
    name : str
        Logger name (usually __name__)
    level : int
        Logging level (logging.INFO, DEBUG, WARNING, ERROR or CRITICAL)
    log_file : Path, optional
        If provided, logs will also be written to this file
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicated handlers
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s] : %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler (handler send logs to the different selected outputs)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    if log_file is not None:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger