
import re
import datetime

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
    time = r'\[(?P<time>\S*)\W.*\]'

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
    def __init__(self, client, timestamp, request, status, size):
        self.client = client

        # self.user_identifier = ''
        # self.user_id = ''

        # from the python docs, %z is a bad directive on some platforms. the
        # time regex has been formated to only capture the date time string
        # before the space and time zone information
        self.time = datetime.datetime.strptime(timestamp, '%d/%b/%Y:%H:%M:%S')

        request_components = request.split(' ')
        self.request = { }
        self.request['method'] = request_components[0]
        self.request['resource'] = request_components[1]
        self.request['protocol'] = request_components[2]

        self.status = None

        self.size = 0

class LogParser(object):
    def __init__(self):
        self.line_regex = _build_w3c_regex()

    def parseLine(self, line):
        match = re.match(self.line_regex, line)
       
        # TODO add some logging here.
        if not match:
            print("no match!")
            return None

        try:
            return LogItem(
                    client=match.group('client'), timestamp=match.group('time'),
                    request=match.group('request'),
                    status=match.group('status'), size=match.group('size'))

        except Exception as e:
            print("error creating log entry %s" % e)
            return None

class LogTail(object):
    def __init__(self, filename):
        self.log = open(filename, 'r')

    def next_line(self):
        new_line = self.log.readline()
        if new_line: return new_line
        else: return None

