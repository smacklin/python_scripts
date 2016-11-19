from urllib import request
import argparse
import datetime
import time
import cmath

'''

Written By Simon Macklin
V1
Date:  26/06/2015

This script will send a request to a web server and records the response time(s).  There are multiple options
from getting the average times, longest and the deviation.

Below is an example to get all results

./web_response.py -u http://example.com -r 200 - s 1 -m -l -d

-s (seconds between the next request)
-r (How many times to repeat a web request
-m (show the average response time
-d ( Show the deviation )
-l ( show the longest response time off all responses collected
-h ( shows some help)

Requires python3 with no third party libs

'''

responses = []

class Log:

    def __init__(self, start_time, finish_time):
        self.start_time = start_time
        self.finish_time = finish_time
        self.response = (start_time - finish_time).microseconds

    def __str__(self):
        return '{0} {1} {2}'.format(self.start_time, self.finish_time, self.response)

    def __add__(self, other):
        return self.response + other.response

def collect_args():
    args = argparse.ArgumentParser()
    args.add_argument('-u', '--url', help='URL of the server testing, format=http://example.com', type=str)
    args.add_argument('-r', '--repeat', help='How many times to repeat a request to a single web server', type=int, default=5)
    args.add_argument('-s', '--seconds', help='Length of time between request', type=int, default=1)
    args.add_argument('-m', '--mean', action='store_true', help='Gets the average response time', default=False)
    args.add_argument('-l', '--longest', action='store_true', help='Gets the longest response time')
    args.add_argument('-d', '--deviation', action='store_true', help='Gets standard deviation')

    return args.parse_args()


def start(args):

    if args.url:
        get_response(args.url, args.repeat, args.seconds)
    else:
        print("Please run the script again with a valid URL")

    if args.mean:
        print('The Average Response Time (ms):\t{0}'.format(mean_time()))
    if args.deviation:
        print('The SD of Response Time (ms):\t{0}'.format(standard_deviation()))
    if args.longest:
        print('The Maximum Response Time (ms):\t{0}'.format(max_time()))


def get_response(url, repeat, seconds):
    url = check_url(url)
    for i in range(repeat):
        try:
            start_time = datetime.datetime.now()
            request.urlopen(url)
            finish_time = datetime.datetime.now()
            responses.append(Log(start_time, finish_time))
            time.sleep(seconds)
        except:
            raise Exception("The Web Server Is Not Responding")


def show_response_times():
    for response in responses:
        print(response)


def standard_deviation():

    count = 0
    total = 0
    total2 = 0

    for response in responses:
        count += 1
        total += response.response
        total2 += (response.response * response.response)

    standard_deviation = cmath.sqrt(total2 - ((total * total) / count))
    return standard_deviation.real


def check_url(url):
    if url.startswith('http://') or url.startswith('https://'):
        return url
    return 'http://' + url


def mean_time():
    length = len(responses)
    total = 0
    for response in responses:
        total += response.response
    return total / length


def max_time():
    max_time = 0
    for response in responses:
        if response.response > max_time:
            max_time = response.response
    return max_time


def main():
    start(collect_args())


if __name__ == '__main__':
    main()

