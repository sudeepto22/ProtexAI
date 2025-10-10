import logging
from pathlib import Path


def setup_logger(name: str, log_dir: str = "/logs") -> logging.Logger:
    """
    Setup and configure a logger with file and console handlers

    Args:
        name: Logger name (e.g., 'Producer', 'Consumer')
        log_dir: Directory to store log files (default: '/logs')

    Returns:
        Configured logger instance
    """
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler = logging.FileHandler(log_path / f"{name.lower()}.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
