import logging
import sys
from config.settings import LOG_DIR, APP_NAME

LOG_FILE = LOG_DIR / "app.log"

def get_logger(name: str = APP_NAME) -> logging.Logger:
    """
    Return a logger that writes to both console and logs/app.log.
    Call this once at the top of any module:

        from config.logger import get_logger
        logger = get_logger(__name__)

    Then use:
        logger.info("Customers generated.")
        logger.warning("Low stock detected.")
        logger.error("Database connection failed.")
    """

    logger = logging.getLogger(name)

    if logger.handlers:
        # Already configured — return as-is to avoid duplicate handlers
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # ── Console handler ───────────────────────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # ── File handler ──────────────────────────────────────────────────────────
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
