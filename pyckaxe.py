import os
import sys
import json
import argparse
import logging
from auth import auth as Auth
from databasehandler import CollectionDatabase
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
from httplib import IncompleteRead

log = logging.getLogger('pyckaxe')
log.setLevel(logging.WARNING)
handler = logging.StreamHandler()
log.addHandler(handler)

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database/')


class StdOutListener(StreamListener):
    # Std Out Listener meant for debugging/testing
    def on_data(self, data):
        print data
        return True

    def on_error(self, status):
        print status


class CollectListener(StreamListener):
    def __init__(self, db, verbose=False):
        super(CollectListener, self).__init__()
        self.db_path = db
        self.db = CollectionDatabase(self.db_path)
        self.verbose = verbose

    def on_data(self, data):
        # Collecting id, favorite count, retweet number, text, coordinates, and
        # user.
        try:
            data = json.loads(data.strip())
            id = data['id_str']
            text = data['text'].strip()
            created_at = data['created_at']
            coords = str(data['coordinates'])
            self.db.add([id, text, created_at, coords])

            if self.verbose:
                sys.stdout.write(
                        '\rTweets collected: %s -- database size: %s kb' %
                                    (self.db.entry_count,
                                    os.path.getsize(self.db_path) >> 10))
                sys.stdout.flush()

        except KeyboardInterrupt:
            log.warning('\nDisconnecting from database...')
            self.db.disconnect_db()
            log.warning('Done.')
            raise

        except KeyError, ke:
            pass

        except Exception, e:
            raise

    def on_error(self, error):
        pass


class Pyckaxe(object):
    def __init__(self, listener, terms, credentials, err_limit=None):
        if not isinstance(listener, StreamListener):
            raise TypeError('Custom listeners must derive from StreamListener.')

        self.listener = listener
        self.terms = terms

        consumer_key = credentials['consumer_key']
        consumer_secret = credentials['consumer_secret']
        access_token = credentials['access_token']
        access_token_secret = credentials['access_secret']

        self.auth = OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_token, access_token_secret)

        self.err_limit = err_limit

    def gather(self):
        stream = Stream(self.auth, self.listener)

        try:
            stream.filter(track=self.terms)

        except IncompleteRead, ir:
            # Incomplete reads occur (as far as the community can tell) when our
            # stream starts falling behind the live feed.
            stream = Stream(self.auth, self.listener)
            stream.filter(track=args.terms)

        except KeyboardInterrupt:
            # TODO: Not sure if I want to do something here.
            raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', help='Provide a database name.')

    parser.add_argument('terms', nargs='+',
                        help='Collect tweets containing the provided term(s).')

    args = parser.parse_args()

    if not args.database:
        args.database = raw_input('Please provide a database name: ')

    db = os.path.join(DATABASE_PATH, args.database)

    listener = CollectListener(db, verbose=True)
    auth = Auth('credentials.csv')

    try:
        pyck = Pyckaxe(listener, args.terms, auth)
        pyck.gather()
    except KeyboardInterrupt:
        log.warning('\nExiting.')
