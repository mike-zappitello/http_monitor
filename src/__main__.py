import os

from log_utils import * 
from monitor import Monitor

if __name__ == '__main__':
    log_filename = os.path.join(
            # '/', 'var', 'log', 'nginx', 'access.log')
            os.path.dirname(__file__), '..', 'test_data', 'access.log')
    logger = LogTail(log_filename)

    monitor = Monitor(logger)
    monitor.start()

