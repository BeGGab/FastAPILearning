import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': 'INFO',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'detailed',
            'filename': 'app.log',
            'maxBytes': 1024 * 1024 * 5, 
            'backupCount': 2,
            'level': 'DEBUG',
        },
    },
    'loggers': {
        'services': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        }
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}

def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)

