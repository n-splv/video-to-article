import logging  # noqa
import logging.config

LOGGER_NAME = "v2a"

CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}},
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        }
    },
    "loggers": {LOGGER_NAME: {"level": "INFO", "handlers": ["stdout"], "propagate": False}},
}

logging.config.dictConfig(CONFIG)

logger = logging.getLogger(LOGGER_NAME)
