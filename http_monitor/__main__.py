import os

from log_utils import * 
from monitor import Monitor
from display import Display

if __name__ == '__main__':
    log_filename = os.path.join(
            # '/', 'var', 'log', 'nginx', 'access.log')
            os.path.dirname(__file__), '..', 'test_data', 'access.log')
    logger = LogTail(log_filename)

    display = Display()

    monitor = Monitor(
            log_item_generator=logger.next_item(), display=display)
    monitor.start()

