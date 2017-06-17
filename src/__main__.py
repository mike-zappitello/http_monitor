import os
import queue
import time
import datetime

from log_utils import * 

if __name__ == '__main__':
    log_filename = os.path.join(
            # '/', 'var', 'log', 'nginx', 'access.log')
            os.path.dirname(__file__), '..', 'test_data', 'access.log')

    # Create a tail of the log filename, a parser to go over it and a timestamp.
    logger = LogTail(log_filename)
    parser = LogParser()
    now = datetime.datetime.now()

    # Create a threshold queue that will hold LogItems in FIFO order. Items will
    # be popped off the top if they are from before now - threshold_delta (aka
    # two minutes ago). Keep a flag on the current threshold status.
    threshold_delta = datetime.timedelta(days=2)
    threshold_queue = queue.Queue()
    threshold = 20
    above_threshold = False

    # Create a display list that will hold LogItems. Everytime now >
    # next_display, show some stats on display list, clear the list, and set
    # next_display to 10 seconds from the last one.
    display_delta = datetime.timedelta(seconds=10)
    next_display = now + display_delta
    display_list = [ ] 

    while True:
        now = datetime.datetime.now()

        threshold_time = now - threshold_delta
        while not threshold_queue.empty() and \
                threshold_queue.queue[0].time < threshold_time:
            _ = threshold_queue.get()

        threshold_size = len(threshold_queue.queue)
        if threshold_size > threshold:
            if not above_threshold:
                above_threshold = True
                message =  \
                        "High traffic generated an alert - hits = %s " \
                        "triggered at %s" % \
                        (threshold_size, now.strftime("%A, %d. %B %Y %I:%M%p"))
                print(message)
        else:
            if above_threshold:
                above_threshold = False
                message = \
                        "Traffic fell back below threshold - hits = %s " \
                        "triggered at %s" % \
                        (threshold_size, now.strftime("%A, %d. %B %Y %I:%M%p"))
                print(message)

        if now > next_display:
            next_display = next_display + display_delta
            print("total log items: %s" % len(display_list))

            # do some processing for display
            for i, item in enumerate(display_list):
                a = "a"

            display_list = [ ]

        line = logger.next_line()
        if line:
            state = parser.parseLine(line)
            if state:
                threshold_queue.put(state)
                display_list.append(state)
        else:
            print(now.strftime("%A, %d. %B %Y %I:%M%p"))
            time.sleep(2)

