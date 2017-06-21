""" HTTP Console Monitor """
import argparse
import curses
import os
import sys

from display import Display
from log_utils import * 
from monitor import Monitor

def parse_args(argv):
    def file_exists_helper(filepath):
        if os.path.exists(filepath): return filepath
        return None

    parser = argparse.ArgumentParser(
            description = 'Consume an actively written-to access log')

    parser.add_argument(
            '-l', '--logfile', dest='logfile', required=True,
            type=file_exists_helper, help='filepath to the access log')

    parser.add_argument(
            '-t', dest='threshold', default=10, type=int,
            help='integer hit frequency threshold in hits per minute')

    parser.add_argument(
            '-f', dest='frequency', default=10, type=int,
            help='integer frequency of status updates in seconds')

    return parser.parse_args(args=argv)

def main(screen, argv):
    args = parse_args(argv)

    logger = LogTail(args.logfile)
    display = Display(screen)

    monitor = Monitor(
            log_item_generator=logger.next_item(), display=display,
            threshold=args.threshold, frequency=args.frequency)

    monitor.start()

if __name__ == '__main__':
    # get argv using sys
    argv = sys.argv[1:]

    # wrap main in curses.wrapper so that terminal will be restored to the
    # origional state should something go wrong.
    curses.wrapper(main, argv)
