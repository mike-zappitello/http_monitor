
import re
from datetime import datetime as datetime # lol

def _build_w3c_regex():
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
    size = r'(?P<size>[0-9]+)'

    return re.compile(
            ip_address + r'\W' + user_identifier + r'\W' + user_id + r'\W' + 
            time + r'\W' + request + r'\W' + status + r'\W' + size)

class LogItem(object):
    def __init__(
            self, client, timestamp, method, resource, protocol, status, size):

        self.client = client
        self.time = timestamp

        self.request = { }
        self.request['method'] = method
        self.request['resource'] = resource
        self.request['protocol'] = protocol

        self.status = status
        self.size = size

class LogParser(object):
    def __init__(self):
        self.line_regex = _build_w3c_regex()

    def parse_line(self, line):
        match = re.match(self.line_regex, line)
       
        # setup the timestamp using datetime
        timestamp = datetime.strptime(
                match.group('timestamp'), '%d/%b/%Y:%H:%M:%S')

        # parse out the request. formated '<method> <resource> <protocol>'
        request = match.group('request').split(' ')

        # convert status and size strings to ints
        status = int(match.group('status'))
        size = int(match.group('size'))

        return LogItem(
                client=match.group('client'), timestamp=timestamp,
                method=request[0], resource=request[1], protocol=request[2],
                status=status, size=size)

class LogTail(object):
    def __init__(self, filename):
        self.log = open(filename, 'r')
        self.parser = LogParser()

    def _parse_next_line(self):
        new_line = self.log.readline()
        if new_line: return self.parser.parse_line(new_line)
        else: return None

    def next_item(self):
        while True:
            try: yield self._parse_next_line()
            except Exception as e: print("error creating log entry %s" % e)
