import logging
import logging.handlers
import datetime
import os

class LogBook():
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    LOGBOOK_LOG_FILE = os.path.join(BASE_DIR, 'logbook')
    log_levels = {'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
            }


    def __init__(self, logger_name='LogBookLogger', log_file_name='logbook.log'):
        # Set up a specific logger with our desired output level
        self.logbook_logger = logging.getLogger(logger_name)
        self.logbook_logger.setLevel(logging.WARNING)

        self.LOGBOOK_LOG_FILE = '/'.join([self.LOGBOOK_LOG_FILE, log_file_name])

        # Add the log message handler to the logger
        self.handler = logging.handlers.RotatingFileHandler(self.LOGBOOK_LOG_FILE, maxBytes=20000, backupCount=5)
        self.logbook_logger.addHandler(self.handler)

    def debug(self, message_time='datetime.datetime.now()', logbook_message='No message provided'):
        self.logbook_logger.debug('~'.join([message_time, 'DEBUG', logbook_message]))

    def info(self, message_time='datetime.datetime.now()', logbook_message='No message provided'):
        self.logbook_logger.info('~'.join([message_time, 'INFO', logbook_message]))

    def warning(self, message_time='datetime.datetime.now()', logbook_message='No message provided'):
        self.logbook_logger.warning('~'.join([message_time, 'WARNING', logbook_message]))

    def error(self, message_time='datetime.datetime.now()', logbook_message='No message provided'):
        self.logbook_logger.error('~'.join([message_time, 'ERROR', logbook_message]))

    def critical(self, message_time='datetime.datetime.now()', logbook_message='No message provided'):
        self.logbook_logger.critical('~'.join([message_time, 'CRITICAL', logbook_message]))

    def set_level(self, log_level='WARNING'):
        try:
            self.logbook_logger.setLevel(self.log_levels[log_level])
        except KeyError:
            self.logbook_logger.setLevel(self.log_levels['WARNING'])

# Loggers to use within views
# djangologbookentry.debug(str(datetime.datetime.now()), 'Your DEBUG message')
# djangologbookentry.info(str(datetime.datetime.now()), 'Your INFO message')
# djangologbookentry.warning(str(datetime.datetime.now()), 'Your WARNING message')
# djangologbookentry.error(str(datetime.datetime.now()), 'Your ERROR message')
# djangologbookentry.critical(str(datetime.datetime.now()), 'Your CRITICAL message')
