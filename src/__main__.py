import os
import queue
import time
import datetime

from log_utils import * 

if __name__ == '__main__':
    log_filename = os.path.join(
            # 'var', 'log', 'nginx', 'access.log'
            os.path.dirname(__file__), '..', 'test_data', 'access.log')

    logger = LogTail(log_filename)
    parser = LogParser()

    threshold = 20
    threshold_queue = queue.Queue()
    display_list = [ ] 

    now = datetime.datetime.now()
    display_delta = datetime.timedelta(seconds=10)
    next_display = now + display_delta
    threshold_delta = datetime.timedelta(minutes=2)

    while True:
        now = datetime.datetime.now()
        threshold_time = now - threshold_delta

        while not threshold_queue.empty() and threshold_queue.queue[0].time < threshold_time:
            _ = threshold_queue.get()

        if len(threshold_queue.queue) > threshold:
            print("OH NO TOO MANY HITS!")

        if now > next_display:
            next_display = now + display_delta
            print("display time!")

            # do some processing for display
            for i, item in enumerate(display_list):
                print(item.request)

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

