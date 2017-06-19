
import time
import unittest

from datetime import datetime as datetime # lol

from http_monitor import monitor 
from http_monitor import log_utils

class MockLogItemGenerator(object):
    def __init__(self, frequency):
        self.frequency = frequency
        self.items_sent = 0

    def next_item(self):
        while self.items_sent < 100:
            if self.items_sent % 10 == 5:
                yield None

            else:
                yield log_utils.LogItem(
                        client='1.2.3.4', timestamp=datetime.now(),
                        method='GET', resource='/sql/index.php',
                        protocol='HTTP/1.1', status=200, size=1234)

            self.items_sent += 1
            time.sleep(self.frequency)
 
class MonitorTest(unittest.TestCase):
    
    def setUp(self):
        self.log_item_generator = MockLogItemGenerator(.5)

    def test_monitor(self):
        self.monitor = monitor.Monitor(self.log_item_generator)
        self.monitor.start()

if __name__ == '__main__': unittest.main()
