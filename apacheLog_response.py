import argparse
import re
import os
import time
import cmath

'''

Written By Simon Macklin

Date:  28/06/2015

This script monitors an apache log file in real time with the parameters you set.  It adds date, source ip and
response time to a dictionary where response times are higher then threshold.

Below is an example to get all results

./apacheLog_response.py -l /var/log/apache/access.log -r 2 -m 5 -d -a

-l (Log path to read) (default 'access.log') for testing
-r (How often to check for changes in seconds
-s (How long to monitor the log file in seconds (default 30 seconds)
-d (Displays last set of records ie the last 10000)
-a (Displays average response time) (default is set to True)
-d (displays standard deviation)
-h ( shows some help)

Requires python3 with no third party libs

'''

''''

Write two "scripts" (and language/approach that you like) as follows:
A script that "watches" the apache log file and only prints out lines that correspond to slow requests (slow being more 1 second) as they are logged
A script that looks at the last 10,000 lines of the file and counts up
average response time
number of responses slower than 100ms, 500ms and 1s respectively
bonus points for giving the standard deviation for (2.a) as well

'''




responses = {}

class LogLine:

    def __init__(self, date, ip, resp):
        self.date = date
        self.ip = ip
        self.response = resp
        self.log_line_count = len(responses) + 1

    def __str__(self):
        return "{0} {1} {2} {3}".format(self.date, self.ip, self.response, self.log_line_count)


def collect_args():
    args = argparse.ArgumentParser()
    args.add_argument('-l', '--log_path', help='The path of the log file', type=str, default='access.log')
    args.add_argument('-s', '--seconds', help='How long to monitor the log file before ending', type=int, default=30)
    args.add_argument('-p', '--lines', help='How many lines to parse', type=int, default=10000)
    args.add_argument('-t', '--threshold', help='Display response times past the threshold set', type=int, default=10000)
    args.add_argument('-a', '--average', action='store_true', help='Displays average response', default=True)
    args.add_argument('-v', '--verbose', action='store_true', help='Shows All Results', default=False)
    args.add_argument('-d', '--deviation', action='store_true', help='Displays standard deviation', default=False)

    return args.parse_args()

def main(args):
    start(args.log_path, args.seconds, args.threshold, args.average, args.deviation, args.verbose)

def decode_log(log_path):
    with open(log_path, 'r') as log:
        lines = log.readlines()
        return lines

def parse_log(lines, threshold):
    for line in lines:
        ip = re.findall(r'\d{1,3}\.\d{1,3}\d{1,3}\.\d{1,3}\.\d{1,3}', line)
        date = re.findall(r'\d{1,2}\/\D{1,3}\/\d{4}:\d{1,2}:\d{1,2}:\d{1,2}', line)
        response = re.findall(r'\d{8,30}', line)

        collect_response_times(date, ip, response, threshold)

def collect_response_times(date, ip, response, threshold):
    if response == []:  #ignore bad data
        pass
    else:
        val = int(response[0])
        if val >= threshold:
            if date[0] in responses.keys():
                pass
            else:
                responses[date[0]] = LogLine(date, ip, val)

def check_last_write(log_name):
    return os.path.getmtime(log_name)

def show_stats():
    for response in responses.values():
        return response

def average_time():
    length = len(responses)
    total = 0
    for response in responses.values():
        total += response.response
    return total / length

def standard_deviation():

    count = 0
    total = 0
    total2 = 0

    for response in responses.values():
        count += 1
        total += response.response
        total2 += (response.response * response.response)

    standard_deviation = cmath.sqrt(total2 - ((total * total) / count))
    return standard_deviation.real

def get_log_count():
    return len(responses)

def get_list_count(lst):
    if isinstance(lst, list):
        return len(lst)

def counter(seconds):
    for i in range(seconds):
        seconds -= 1
        print('*')
        time.sleep(1)
    return seconds


def start(log_path, monitor_time, threshold, average, sd, verbose):

    print("Reading Log For {0} Seconds".format(monitor_time))
    start_time = os.path.getmtime(log_path)
    parse_log(decode_log(log_path), threshold)

    if verbose:
        print(show_stats())
        print("Collected {0} Log Records".format(get_log_count()))

    while counter(monitor_time):
        if start_time < check_last_write(log_path):
            start_time = check_last_write(log_path)
            print('yoop')
            parse_log(decode_log(log_path), threshold)

            if verbose:
                print(show_stats())
                print("Collected {0} Log Records".format(get_log_count()))

    if average:
        print("The Average Response Recorded Was {0} (ms)".format(average_time()))

    if sd:
        print("The Standard Deviation Recorded Was {0} (ms)".format(standard_deviation()))



if __name__ == '__main__':
    main(collect_args())
