
import time

from datetime import datetime as datetime   # lol
from datetime import timedelta as timedelta 
from queue import Queue as Queue            # lol

class Monitor(object):
    class _Alert(object):

        def __init__(self, start_time):
            self.start_time = start_time
            self.end_time = None 
            self.hits = 1

        def active(self): return self.end_time == None
        def add_hit(self): self.hits += 1
        def end(self, end_time): self.end_time = end_time

        def duration(self):
            if self.end_time: return self.end_time - self.start_time
            return datetime.now() - self.start_time

        def ongoing(self):
            if self.end_time: return True
            return False


    def __init__(
            self, log_item_generator, display, threshold=2, frequency=2,
            verbose=False):

        self.log_item_generator = log_item_generator
        self.display = display
        display.set_monitor(self)
        self.verbose = verbose

        # get the current time to base our triggers off of
        self.now = datetime.now()

        # Create a threshold queue that will hold LogItems in FIFO order. Items
        # will # be popped off the top if they are from before two minutes ago.
        # Keep a flag on the current threshold status.
        self.threshold_delta = timedelta(minutes=2)
        self.threshold_queue = Queue()
        self.threshold = threshold
        self.alerts = [ ] 

        # Create a display list that will hold LogItems. Everytime the event
        # loop crosses the next_display time,  show some stats on display list,
        # clear the list, and set next_display to 10 seconds from the last one.
        self.display_delta = timedelta(seconds=frequency)
        self.next_display = self.now + self.display_delta
        self.stats_list = [ ] 

        self.pre_populate_data()

    def __log(self, message):
        if self.verbose: print(message)

    def get_latest_alert(self): return self.alerts[-1]

    def active_alert(self):
        if len(self.alerts) > 0 and self.alerts[-1].active():
            return self.alerts[-1]
        return None

    def prune_threshold_queue(self, threshold_time):
        # pop off elements of the queue from before threshold_time.
        #
        # if an alert has been started, end it if the queue falls below the
        # threshold size
        while not self.threshold_queue.empty() and \
                self.threshold_queue.queue[0].time < threshold_time:

            self.__log('pop off hit')

            # pop off expired item
            expired_item = self.threshold_queue.get()

            if self.active_alert() and  self.threshold_queue.qsize() > self.threshold:
                self.active_alert().end(
                        expired_item.time - self.threshold_delta)
                self.display.low_traffic_alert()

    def pre_populate_threshold(self, log_item):
        self.threshold_queue.put(log_item)
        self.prune_threshold_queue(log_item.time - self.threshold_delta)

        # if the threshold is newly surpassed create an event
        if self.threshold_queue.qsize() > self.threshold:
            if self.active_alert(): self.active_alert().add_hit()
            else: 
                self.alerts.append(self._Alert(log_item.time))
                self.display.high_traffic_alert()

    def populate_threshold(self, log_item):
        if log_item: self.threshold_queue.put(log_item)

        # assuming with self.now that the log times are using the same clock as
        # the application parsing the logs. if that assumption is false,
        # self.now should be adjusted by the offset between the two.
        self.prune_threshold_queue(self.now - self.threshold_delta)

        # if the threshold is newly surpassed create an event this will only
        # happen if log item is added
        if self.threshold_queue.qsize() > self.threshold:
            if self.active_alert(): self.active_alert().add_hit()
            else: 
                self.alerts.append(sel._Alert(log_item.time))

    def update_display(self):
        self.display.log_items = self.stats_list
        self.display.update_display()

    def pre_populate_data(self):
        # get the first item from the log generator. there may be multiple lines
        # in the log file before the monitor began watching it. the monitor
        # should take an account of each of those items before watching for
        # new log items
        log_item = next(self.log_item_generator)
        while log_item:
            # prepopulate the threshold queue and status list with the log item
            self.pre_populate_threshold(log_item)

            # if the log item occured within our stats window, add it to the
            # stats list.
            if log_item.time > self.now - self.display_delta:
                self.stats_list.append(log_item)

            # then get the next log item
            log_item = next(self.log_item_generator)

        # update the display
        self.update_display()

    def start(self):
        while True:
            go_to_sleep = False
            self.now = datetime.now()

            log_item = next(self.log_item_generator)
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
                # self.__log('zzz')
                time.sleep(1)
