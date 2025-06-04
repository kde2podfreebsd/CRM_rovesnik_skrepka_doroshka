import logging
import sys
from enum import Enum
import os


class LogLevel(str, Enum):
    DEBUG = 'debug'
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
    CRITICAL = 'critical'


class ApplicationLogger:
    def __init__(self, log_to_file=False):
        basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        self.logs_dirPath = f"{basedir}/logs/"
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        os.makedirs(self.logs_dirPath, exist_ok=True)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s')

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        if log_to_file:
            self.log_file_path = f'{self.logs_dirPath}app_log.log'
            file_handler = logging.FileHandler(self.log_file_path)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        self.module_handlers = {}

    def add_module_handler(self, module_name):
        if module_name not in self.module_handlers:
            log_file_path = f'{self.logs_dirPath}{module_name}_log.log'
            file_handler = logging.FileHandler(log_file_path)
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s'))
            self.module_handlers[module_name] = file_handler
            self.logger.addHandler(file_handler)

    def log(self, level, message, module_name=None):
        if module_name:
            if module_name not in self.module_handlers:
                self.add_module_handler(module_name)
            self.logger.addHandler(self.module_handlers[module_name])

        if level == LogLevel.DEBUG:
            self.logger.debug(message)
        elif level == LogLevel.INFO:
            self.logger.info(message)
        elif level == LogLevel.WARNING:
            self.logger.warning(message)
        elif level == LogLevel.ERROR:
            self.logger.error(message)
        elif level == LogLevel.CRITICAL:
            self.logger.critical(message)
        else:
            raise ValueError("Invalid log level")

        if module_name:
            self.logger.removeHandler(self.module_handlers[module_name])


if __name__ == "__main__":
    logger = ApplicationLogger(log_to_file=True)

    logger.log('info', 'This is an informational message.')
    logger.log('warning', 'This is a warning message.')

    logger.log('error', 'Error in module1.', module_name='head_bot')
