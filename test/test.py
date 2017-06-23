
import re
import time
import unittest

from datetime import datetime as datetime   # lol
from datetime import timedelta as timedelta 
from itertools import *
from queue import Queue as Queue            # lol

from http_monitor import monitor 
from http_monitor import log_utils
from http_monitor import display

def LOG(message):
    if True: print(message)

class MockLogItemGenerator(object):
    def __init__(self):
        self.schedule = [ ] 
        self.items_sent = 0

    def set_schedule(self, schedule): self.schedule = schedule

    def generate_item(self, time):
        self.items_sent += 1
        return log_utils.LogItem(
                client='1.2.3.4', timestamp=time, method='GET',
                resource='/sql/index.php', protocol='HTTP/1.1', status=200,
                size=1234)

    def next_item(self):
        for time in self.schedule:
            while datetime.now() < time: yield None
            # LOG('item: %s' % time)
            yield self.generate_item(time)

class MockDisplay(object):

    class _Expected_Alert(object):
        def __init__(self, time):
            self.expected_start = time
            self.expected_end = None

        def __assert_similar_time(self, expected, real):
            LOG("expected: %s" % expected)
            LOG("real:     %s" % real)
            assert(real.hour == expected.hour)
            assert(real.minute == expected.minute)
            assert(real.second == expected.second)

        def set_end(self, time):
            self.expected_end = time

        def start(self, time):
            self.__assert_similar_time(self.expected_start, time)

        def end(self, time):
            self.__assert_similar_time(self.expected_end, time)

    def __init__(self):
        self.expected_alerts = Queue()
        self.display_updates = 0
        self.monitor = None
        self.threshold = 1

    def set_schedule(self, schedule, threshold, threshold_s):
        '''
        Iterates through a schedule of times, using the threshold and the
        threshold_s (time a threshold is going to be watched for) to create a
        queue of alerts a monitor is going to be expected to trigger.
        '''

        length = timedelta(seconds=threshold_s, microseconds=5)
        alert = None

        head = 0
        tail = 0

        while head < len(schedule):
            LOG("[%s]: %s" % (head, schedule[head]))
            LOG("p - h:%s, t:%s" % (head, tail))
            while schedule[head] - schedule[tail] > length:
                LOG("w - h:%s, t:%s" % (head, tail))
                tail += 1
                if head - 1 - tail < threshold and alert:
                    LOG("alert off - %s" % (schedule[tail] + length))
                    alert.set_end(schedule[tail] + length)
                    self.expected_alerts.put(alert)
                    alert = None

            if head - tail + 1 >= threshold and alert == None:
                LOG("alert on  - %s" % schedule[head])
                alert = self._Expected_Alert(schedule[head])

            head += 1

        if alert:
            self.expected_alerts.put(alert)
            return 1

        return 0

        LOG("\start with %s alerts\n" % self.expected_alerts.qsize())

    def set_monitor(self, monitor):
        self.monitor = monitor

    def high_traffic_alert(self):
        LOG('high traffic')
        real = self.monitor.get_latest_alert()
        expected = self.expected_alerts.queue[0]

        expected.start(real.start_time)

    def low_traffic_alert(self):
        LOG('low traffic')
        real = self.monitor.get_latest_alert()
        expected = self.expected_alerts.get()

        expected.end(real.end_time)

    def update_display(self):
        LOG("currently %s alerts left" % self.expected_alerts.qsize())

class MonitorTest(unittest.TestCase):
    
    def setUp(self):
        self.log_item_generator = MockLogItemGenerator()
        self.display = MockDisplay()

    def create_schedule(self, timedeltas):
        now = datetime.now()
        return [ now + timedelta(seconds=seconds) for seconds in timedeltas ]

    def run_alert_test(self, schedule, threshold, threshold_s):
        self.log_item_generator.set_schedule(schedule)

        active_alerts = self.display.set_schedule(
                schedule, threshold, threshold_s)

        try:
            self.monitor = monitor.Monitor(
                    self.log_item_generator.next_item(), self.display,
                    threshold=threshold, threshold_s=threshold_s, frequency=10)
            self.monitor.start()
        except StopIteration as e: _ = 'we reached the end of the schedule'

        self.assertEqual(self.display.expected_alerts.qsize(), active_alerts)

    def test_monitor(self):
        timedeltas = [ 0, 0, 2, 4, 6, 8, 10, 30 ]

        self.run_alert_test(
            schedule = self.create_schedule(timedeltas), threshold = 5,
            threshold_s = 10)

    def test_multiple_prealerts(self):
        timedeltas = [
                -20, -20, -20, -20, -20,    # 5 quick events to create an alert
                -10,                        # enough time to let them go
                -5, -5, -5, -5 ]            # trigger another alert

        print(len(timedeltas))

        self.run_alert_test(
            schedule = self.create_schedule(timedeltas), threshold = 5,
            threshold_s = 10)

    def test_recent_prealerts(self):
        timedeltas = [
                -4, -3, -2, -2, -2,         # prime logs with early events
                1, 1.5, 2, 2.5, 3, 4,       # trigger while running
                10, 12, 14, 16 ]            # puase and trigger another alert

        schedule = self.create_schedule(timedeltas)
        self.run_alert_test(schedule, threshold=6, threshold_s=6)

    def test_for_scale(self):
        def pred(x):
            if x < 1000: return True
            elif x < 3000: return False
            elif x < 4500: return True

        def stop(x): return x < 5000


        timedeltas = [ s * 0.015 for s in takewhile(stop, count(1)) if pred(s) ]

        schedule = self.create_schedule(timedeltas)
        self.run_alert_test(schedule, threshold=100, threshold_s=10)

class ParserTest(unittest.TestCase):

    def setUp(self):
        self.line_regex = log_utils.build_w3c_regex()

    def parse_line_for_url(self, line):
        LOG(line)

        match = re.match(self.line_regex, line)
        self.assertIsNotNone(match, "Could not match line: %s" % line)

        url = match.group('request').split(' ')[1]
        LOG(url)

        section = log_utils.parse_section(url) 
        LOG(section)

        self.assertIsNotNone(section)
        LOG('')

    def test_log_line_parseing(self):
        lines = [
            '240.200.12.8- - [28/Aug/1995:00:00:38 -0400] "GET http://www.google.com/pub/atomicbk/catalog/logo2.gif HTTP/1.0" 200 12871',
            '46.246.37.67 - - [11/Jun/2017:13:00:01 +0000] "GET //pma/scripts/setup.php HTTP/1.1" 404 142 "-" "-"',
            '46.246.37.67 - - [11/Jun/2017:13:00:01 +0000] "GET http://www.datadog.com/ HTTP/1.1" 404 142 "-" "-"',
	    '123.45.67.8 - - [28/Aug/1995:00:01:52 -0400] "GET http://www.facebook.com/pub/tblake/www/aacc.gif HTTP/1.0" 304 -',
	    '123.45.67.8 - - [28/Aug/1995:00:01:15 -0400] "GET http://www.facebook.com/pub/alweiner/cgi-bin/homepage.cgi?game HTTP/1.0" 200 -',
        ]

        for line in lines:
            with self.subTest():
                self.parse_line_for_url(line)


if __name__ == '__main__': unittest.main()
