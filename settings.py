import os
from logging.config import dictConfig
from pathlib import Path

from dotenv import load_dotenv

# project path ############
PROJECT_PATH = Path(__file__).parent

# dotenv ############
env_path = PROJECT_PATH / '.env'
load_dotenv(dotenv_path=env_path, verbose=True)

# Downloaded issues directory
ISSUES_PATH = 'issues'
IMAGES_PATH = 'images'

# GitHub authentication ############
GITHUB_USER = os.getenv('GITHUB_USER', '')
GITHUB_PASSWORD = os.getenv('GITHUB_PASSWORD', '')

# logging #############
LOG_DIR = PROJECT_PATH / 'log'
LOG_DIR.mkdir(parents=True, exist_ok=True)
dictConfig({
    'disable_existing_loggers': False,
    'version': 1,
    'formatters': {
        'verbose': {
            'format':
                '%(levelname)s %(asctime)s %(name)s %(funcName)s %(lineno)d %(process)d %(threadName)s - %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'verbose',
            'when': 'D',
            'interval': 1,
            'filename': f'{LOG_DIR}/command.log'
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ["file", "console"],
    },
})
