
import curses
import logging

from datetime import datetime as datetime # lol
from itertools import *

class Display(object):

    def __init__(self, screen):
        self.time_fmt = "%d.%B.%Y %I:%M%p"
        self.monitor = None
        self.latest_hits = [ ]

        self.screen = screen
        self.width = curses.COLS - 1
        self.y = 0

        self._init_screen()

    def _init_screen(self):
        # clear the screen
        self.screen.clear()

        # add a row of stars on the top row of the monitor
        self._add_full_row(self.y)
        self.y += 1

        # add a centered title for the monitor
        self.screen.addstr(self.y, 0, "*")
        title = "HTTP Traffic Monitor"
        self.screen.addstr(self.y, int(self.width/2 - len(title)/2), title)
        self.screen.addstr(self.y, self.width - 1, "*")
        self.y += 1

        # add a row of fulls below the title
        self._add_full_row(self.y)
        self.y += 1

        # add an alerts table header
        self._add_to_table(
                self.y, "Alerts", "Started", "Ended", "Hits per Minute")
        self.y += 1

        # add a row of fulls below the alerts table header
        self._add_full_row(self.y)
        self.y += 1

        # add an empty row to the table
        self._add_to_table(self.y)

        self.screen.refresh()

    def _add_full_row(self, y, char="*"):
        for x in range(0, self.width): self.screen.addstr(y, x, char)

    def _add_to_table(self, y, col1='', col2='', col3='', col4=''):
        col_width = int(self.width / 4) - 1
        xs = [ n + n * col_width for n in range(0, 5) ]

        for x in xs: self.screen.addstr(y, x, "*")

        # if column string, clear out all the column and add the string
        if col1:
            for x in range(xs[0] + 1, xs[1]): self.screen.addstr(y, x, " ")
            start_x = int(((xs[0] + xs[1]) / 2) - len(col1) / 2)
            self.screen.addstr(y, start_x, col1)

        if col2:
            for x in range(xs[1] + 1, xs[2]): self.screen.addstr(y, x, " ")
            start_x = int(((xs[1] + xs[2]) / 2) - len(col2) / 2)
            self.screen.addstr(y, start_x, col2)

        if col3:
            for x in range(xs[2] + 1, xs[3]): self.screen.addstr(y, x, " ")
            start_x = int(((xs[2] + xs[3]) / 2) - len(col3) / 2)
            self.screen.addstr(y, start_x, col3)

        if col4:
            for x in range(xs[3] + 1, xs[4]): self.screen.addstr(y, x, " ")
            start_x = int(((xs[3] + xs[4]) / 2) - len(col4) / 2)
            self.screen.addstr(y, start_x, col4)

    def _get_popular_section(self):
        if len(self.latest_hits) == 0: return '  (0)'

        # sort the list, group them, and find the max one
        most_popular = ''
        largest_size  = 0
        for item, group in  groupby(sorted(self.latest_hits)):
            size = len(list(group))
            if size > largest_size:
                largest_size = size
                most_popular = item.get_section()

        return most_popular

    def _get_accumulated_size(self):
        return sum(li.size for li in self.latest_hits)

    def set_monitor(self, monitor):
        self.monitor = monitor 
        self.update_display()

    def high_traffic_alert(self):
        alert = self.monitor.get_latest_alert()
        time = alert.start_time.strftime(self.time_fmt)
        hpm = "{0:.4f}".format(alert.hits / alert.duration().seconds * 60)

        self._add_to_table(self.y, col2=time, col3="ONGOING", col4=hpm)
        self.update_display()

    def low_traffic_alert(self):
        alert = self.monitor.get_latest_alert()
        time = alert.end_time.strftime(self.time_fmt)
        hpm = "{0:.4f}".format(alert.hits / alert.duration().seconds * 60)

        self._add_to_table(self.y, col3=time, col4=hpm)
        self.y += 1

        self.update_display()

    def update_display(self):
        popular = self._get_popular_section()
        size = self._get_accumulated_size()

        # clear the bottom of our screen
        for row in range(1, 6): self._add_full_row(self.y + row, char=" ")

        self._add_full_row(self.y + 2)
        self.screen.addstr(self.y + 4, 0, "Popular Section: %s" % popular)
        self.screen.addstr(self.y + 5, 0, "Total Size Downloaded: %s" % size)
        self.screen.addstr(self.y + 6, 0, "Time: %s" % datetime.now()) 

        self.screen.refresh()
