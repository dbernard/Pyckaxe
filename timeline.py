import os
import re
import string
import argparse
import plotly.plotly as py
from auth import auth
from plotly.graph_objs import *
from datetime import datetime
from databasehandler import CollectionDatabaseReader

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database/')


class Timeline(object):
    def __init__(self):
        self.times = []

    def add_time(self, time):
        # time is expected to be a datetime object
        self.times.append(time)

    def get_results(self, time_delta, title):
        # Start with first time value
        start = self.times[0]
        count = 0

        # x and y axis values - x will be datetime objects, y will be counts
        x = []
        y = []

        # Build our graph data set
        for time in self.times:
            if (time - start).total_seconds() < time_delta:
                count += 1
            else:
                x.append(start)
                y.append(count)
                start = time
                count = 1

        return self._graph_timeline(x, y, title)

    def _graph_timeline(self, times, counts, title):
        creds = auth('credentials.csv')

        plotly_username = creds['plotly_username']
        plotly_key = creds['plotly_api_key']

        py.sign_in(plotly_username, plotly_key)

        data = Data([
            Scatter(
                x = times,
                y = counts
                )
            ])

        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        fname = ''.join(c for c in title if c in valid_chars)

        plot_url = py.plot(data, filename=fname)
        py.image.save_as({'data' : data}, 'images/%s.png' % fname)

        return plot_url, fname


def getTimeline(db, time_delta, title):
    tl = Timeline()
    times = db.get_all_timestamps()
    for time in times:
        t = time[0]
        ptrn = r"(\w{3} \w{3} \d{2} \d{2}:\d{2}:\d{2}) (?:[\+|\-]\d{4}) (\d{4})"
        time = re.findall(ptrn, t)
        converted_time = datetime.strptime(' '.join(time[0]),
                                           '%a %b %d %H:%M:%S %Y')
        tl.add_time(converted_time)

    return tl.get_results(time_delta, title)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', help='Provide a database name.')
    parser.add_argument('--timedelta', help='The time in seconds between graph' +
                                            ' x values.')
    parser.add_argument('--title', help='Graph title.')

    args = parser.parse_args()

    if not args.database:
        args.database = raw_input('Please provide a database name: ')

    if not args.timedelta:
        args.timedelta = raw_input('Please provide a time delta value: ')

    if not args.title:
        args.title = raw_input('Please provide a graph title: ')

    db = CollectionDatabaseReader(os.path.join(DATABASE_PATH, args.database))

    url, fname = getTimeline(db, int(args.timedelta), args.title)

    print 'Timeline plotted.\nURL: %s\nImage: %s' % (url,
                                                    'images/%s.png' % fname)

    db.disconnect_db()
