
import logging
import os
import re

from datetime import datetime as datetime # lol

log_dir = os.path.join('logs')
if not os.path.exists(log_dir): os.makedirs(log_dir)

log_file = os.path.join('logs', 'meta.log')
logging.basicConfig(filename=log_file, filemode='w+')

def build_w3c_regex():
    # ip addresses consist 4 dot seperated numbers that fall between 0 and 255
    # without any leading zeros
    ip_num = r'(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])'
    dot = r'\.'
    ip_address = (
            r'(?P<client>' +
            ip_num + dot + ip_num + dot + ip_num + dot + ip_num +
            ')')

    # assume both of these are just not whitespace
    user_identifier = r'(?P<user_identifier>\S*)'
    user_id = r'(?P<user_id>\S*)'

    # assume the time is everything between [ and ]. datetime will validate the
    # format later
    time = r'\[(?P<timestamp>\S*)\W.*\]'

    # assume the request is everything between " and ". validate later.
    request = r'\"(?P<request>.*)\"'

    # valid status codes will range between 100 and 599
    status = r'(?P<status>[1-5][0-9][0-9])'

    # size is an int
    size = r'(?P<size>[0-9]+|-)'

    return re.compile(
            ip_address + r'\W' + user_identifier + r'\W' + user_id + r'\W' + 
            time + r'\W' + request + r'\W' + status + r'\W' + size)

def parse_section(url):
    try:
        # rip off everything before the two forward slashes.
        index = url.find('//')
        the_rest = url[index + 2 : -1]

        # if left with nothing, return None
        if the_rest == '': return '' 

        # easiest way i could use to find indecies of all '/' chars
        forward_slashes  = [ i for i, ch in enumerate(the_rest) if ch == '/']

        # if less than two '/' chars, we're done.
        if len(forward_slashes) < 2 : return the_rest

        index = forward_slashes[1]
        return the_rest[0 : index]

    except Exception as e:
        logging.error("Error parsing url for section:\n%s" % url)
        return  ''

class LogItem(object):
    def __init__(
            self, client, timestamp, method, resource, protocol, status, size):

        self.client = client
        self.time = timestamp

        self.request = { }
        self.request['method'] = method
        self.request['resource'] = resource
        self.request['protocol'] = protocol

        self.section = None

        self.status = status
        self.size = size

    def __lt__(self, y):
        ''' built in function for sorting '''
        return self.get_section() < y.get_section()

    def get_section(self):
        '''
        get the section item from the request resource url. if it exists, cache
        it. if it doesn't, cache an empty string.
        '''
        if self.section: return self.section

        self.section = parse_section(self.request['resource'])
        return self.section

class LogTail(object):
    def __init__(self, filename):
        self.log = open(filename, 'r')
        self.line_regex = build_w3c_regex()
        self.new_line = None

    def _parse_next_line(self):
        '''
        get the next line from the log. if a new line has appeared return a new
        LogItem. if not, return None
        '''
        self.new_line = self.log.readline()
        if self.new_line:
            match = re.match(self.line_regex, self.new_line)
           
            # setup the timestamp using datetime
            timestamp = datetime.strptime(
                    match.group('timestamp'), '%d/%b/%Y:%H:%M:%S')

            # parse out the request. formated '<method> <resource> <protocol>'
            request = match.group('request').split(' ')

            # convert status and size strings to ints
            status = int(match.group('status'))

            # size might be a string digit or -
            size = match.group('size')
            if size == '-': size = 0
            else: size = int(size)

            return LogItem(
                    client=match.group('client'), timestamp=timestamp,
                    method=request[0], resource=request[1], protocol=request[2],
                    status=status, size=size)
        else:
            return None

    def next_item(self):
        ''' 
        generator function for accessing the next item in the log as it appears. 

        wrap in a try except block that will log exceptions as the are raised.
        they will most likely be parsing errors from bad log lines or borked
        parsing.
        '''
        while True:
            try: yield self._parse_next_line()
            except Exception as e:
                logging.error("Encountered error\n\t%s\n\t%s" % (self.new_line, e))
