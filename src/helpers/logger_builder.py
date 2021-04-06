# -*- coding: utf-8 -*-

from pathlib import Path
from src.helpers.Errors import NotLogDir


def config(log_dir, ip):

    res = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
               'filter': 'simple',
               'format': '%(asctime)s;%(name)s;%(filename)s;%(funcName)s;%(message)s;',
                'datefmt': '%m.%d.%Y %H:%M:%S',
            }

        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'CRITICAL',
                'formatter': 'simple',
                'stream': 'ext://sys.stdout'

            },
        },

        'loggers': {
            f'{ip}': {
                'level': 'INFO',
                'handlers': ['console', ],
                'propagate': 'no'
            }
        }

    }

    if log_dir:

        p = Path(log_dir)
        if not p.exists():
            raise NotLogDir(f'the dir name {p.absolute()} does not exist')

        res['handlers'].update(
            {
                    'into_file_handler': {
                        'class': 'logging.handlers.RotatingFileHandler',
                        'level': 'DEBUG',
                        'formatter': 'simple',
                        'filename': p / (ip + '.log'),
                        'maxBytes': 10485760,
                        'backupCount': 20,
                        'encoding': 'utf-8',
                    }
            }
        )

        res['loggers'][f'{ip}']['handlers'].append('into_file_handler')

    return res
