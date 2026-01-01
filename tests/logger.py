from microtpct.utils import setup_logger

logger = setup_logger(__name__, log_file="logs/test.log", level=10)

logger.debug('debug message')
logger.info('info message')
logger.warning('warn message')
logger.error('error message')
logger.critical('critical message')