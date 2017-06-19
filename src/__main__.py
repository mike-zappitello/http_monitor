import os
import queue
import time

from datetime import datetime as datetime # lol
from datetime import timedelta as timedelta 

from log_utils import * 

class Monitor(object):
    def __init__(self, log_item_generator):
        # object that will generate log items for display
        self.log_item_generator = log_item_generator

        # get the current time to base our triggers off of
        self.now = datetime.now()

        # Create a threshold queue that will hold LogItems in FIFO order. Items
        # will # be popped off the top if they are from before two minutes ago.
        # Keep a flag on the current threshold status.
        self.threshold_delta = timedelta(minutes=2)
        self.threshold_queue = queue.Queue()
        self.threshold = 2
        self.above_threshold = False
        self.threshold_crosses = [ ]

        # Create a display list that will hold LogItems. Everytime the event
        # loop crosses the next_display time,  show some stats on display list,
        # clear the list, and set next_display to 10 seconds from the last one.
        self.display_delta = timedelta(seconds=10)
        self.next_display = self.now + self.display_delta
        self.stats_list = [ ] 

        self.pre_populate_data()

    def get_threshold_time(self, log_item):
        if log_item: return log_item.time - self.threshold_delta
        return self.now - self.threshold_delta

    def high_traffic_alert(self, start_time):
        message =  "HIGH TRAFFIC ALERT\n\tHits = %s\n\tTriggered at %s" % \
                (
                    len(self.threshold_queue.queue),
                    start_time.strftime("%A, %d. %B %Y %I:%M%p")
                )
        print(message)

    def low_traffic_alert(self, expired_time):
        message = "TRAFFIC ALERT OVER\n\tTriggered at %s" % \
                expired_time.strftime("%A, %d. %B %Y %I:%M%p")
        print(message)

    def display_stats(self):
        print("display stat")
        # do some processing for display
        for i, item in enumerate(self.stats_list):
            a = "a"

    def prune_threshold_queue(self, threshold_time):
        # pop off elements of the queue from before threshold_time.
        #
        # if an alert has been started, end it if the queue falls below the
        # threshold size
        while not self.threshold_queue.empty() and \
                self.threshold_queue.queue[0].time < threshold_time:

            # pop off expired item
            expired_item = self.threshold_queue.get()

            if self.above_threshold and self.threshold_queue.qsize() > self.threshold:
                self.above_threshold = False
                self.low_traffic_alert(expired_item.time + self.threshold_delta)

    def pre_populate_threshold(self, log_item):
        self.threshold_queue.put(log_item)
        self.prune_threshold_queue(log_item.time - self.threshold_delta)

        # if the threshold is newly surpassed create an event
        if self.threshold_queue.qsize() > self.threshold and not self.above_threshold:
            self.above_threshold = True
            self.high_traffic_alert(log_item.time)

    def populate_threshold(self, log_item):
        if log_item: self.threshold_queue.put(log_item)

        # assuming with self.now that the log times are using the same clock as
        # the application parsing the logs. if that assumption is false,
        # self.now should be adjusted by the offset between the two.
        self.prune_threshold_queue(self.now - self.threshold_delta)

        # if the threshold is newly surpassed create an event this will only
        # happen if log item is added
        if self.threshold_queue.qsize() > self.threshold and not self.above_threshold:
            self.above_threshold = True
            self.high_traffic_alert(log_item.time)

    def update_display(self):
        print('update display!')

    def pre_populate_data(self):
        # get the first item from the log generator. there may be multiple lines
        # in the log file before the monitor began watching it. the monitor
        # should take an account of each of those items before watching for
        # new log items
        log_item = self.log_item_generator.next_item()
        while log_item:
            # prepopulate the threshold queue and status list with the log item
            self.pre_populate_threshold(log_item)

            # if the log item occured within our stats window, add it to the
            # stats list.
            if log_item.time > self.now - self.display_delta:
                self.stats_list.append(log_item)

            # then get the next log item
            log_item = self.log_item_generator.next_item()

        # update the display
        self.update_display()


    def start(self):
        while True:
            go_to_sleep = False
            self.now = datetime.now()

            log_item = self.log_item_generator.next_item()
            if log_item: self.stats_list.append(log_item)
            else: go_to_sleep = True

            self.populate_threshold(log_item)

            # update the display if its time
            if self.now > self.next_display:
                self.update_display()

                # reset the next display time and the stats list
                self.next_display = self.next_display + self.display_delta
                self.stats_list = [ ]

            if go_to_sleep:
                print('zzz')
                time.sleep(1)

if __name__ == '__main__':
    log_filename = os.path.join(
            # '/', 'var', 'log', 'nginx', 'access.log')
            os.path.dirname(__file__), '..', 'test_data', 'access.log')
    logger = LogTail(log_filename)

    monitor = Monitor(logger)
    monitor.start()

