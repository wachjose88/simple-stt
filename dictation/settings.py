from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s '
                      '%(module)s.%(funcName)s.%(funcName)s():%(lineno)d  '
                      '"%(message)s"',
            'datefmt': '%d/%b/%Y %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'dictation.log',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'dictation.app': {
            'handlers': ['console'],
            'level': 'DEBUG'
        },
        'dictation.stt': {
            'handlers': ['console'],
            'level': 'DEBUG'
        },
    }
}
