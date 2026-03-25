# MIT License
#
# Copyright (c) 2026 Josef Wachtler
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""This module holds the main settings of the app.

BASE_DIR: The base folder of the app.

LOGGING_CONFIG: The configuration of the logger.
There are two loggers:
    - dictation.app: the logger for the UI
    - dictation.stt: the logger for speech recognition
"""
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
