import logging.config
from src.server.config import Settings
import re
from pathlib import Path
import configparser

settings = Settings()

config = configparser.ConfigParser()
config.read(settings.APP_FILES_PATH / 'logger.ini')

if 'handler_fileHandler' in config.sections():
    """ If path is just a filename, change it to full path (APP_FILES_PATH/filename) """
    old_file_path = re.match(r'(\()(["\'](.*?)["\'])(,.*\))', config['handler_fileHandler']['args'])[3]
    old_file_name = Path(old_file_path).name

    if old_file_path == old_file_name:
        new_file_path = str(settings.APP_FILES_PATH / old_file_name)
        match = re.match(r'(\()(["\'].*["\'])(,.*\))', config['handler_fileHandler']['args'])
        config.set('handler_fileHandler', 'args',
                   f'{match.group(1)}"{new_file_path}"{match.group(3)}')

logging.config.fileConfig(
    config,
    disable_existing_loggers=False,
)

logger = logging.getLogger(__name__)
