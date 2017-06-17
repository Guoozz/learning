import logging.config
from log.test import some_func


LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {
            "format": "[%(levelname)-7s %(asctime)s %(name)s  %(filename)s %(lineno)s] %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "level": "DEBUG",
            "stream": "ext://sys.stdout"
        }
    },
    "loggers": {
        "a": {
            "handlers": ["console"],
            "level": "DEBUG"
        },
        "a.c": {
            "level": "DEBUG",
            "propagate": True
        }
    }

}


logging.config.dictConfig(LOGGING)

