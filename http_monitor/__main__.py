""" HTTP Console Monitor """
import argparse
import sys
import os

from log_utils import * 
from monitor import Monitor
from display import Display

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

    parser.add_argument(
            '-v', '--verbose', dest='verbose', default=False,
            action='store_true', help='verbose logging')

    return parser.parse_args(args=argv)

def main(argv):
    args = parse_args(argv)

    print(args)

    logger = LogTail(args.logfile)
    display = Display()

    monitor = Monitor(
            log_item_generator=logger.next_item(), display=display,
            threshold=args.threshold, frequency=args.frequency,
            verbose=args.verbose)

    monitor.start()

if __name__ == '__main__': main(argv=sys.argv[1:])
