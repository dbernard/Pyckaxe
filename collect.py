import os
import sys
import json
from auth import auth
from databasehandler import CollectionDatabase
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

DATABASE_PATH = 'database/tweets.db'

auth = auth('credentials.csv')

consumer_key = auth['consumer_key']
consumer_secret = auth['consumer_secret']

access_token = auth['access_token']
access_token_secret = auth['access_secret']

db = CollectionDatabase(DATABASE_PATH)


class CollectListener(StreamListener):
    def on_data(self, data):
        # Collecting id, favorite count, retweet number, text, coordinates, and
        # user.
        try:
            data = json.loads(data.strip())
            id = data['id_str']
            fav_count = data['favorite_count']
            retweets = data['retweet_count']
            text = data['text'].strip()
            coords = str(data['coordinates'])
            user = data['user']
            db.add([id, fav_count, retweets, text, coords])

            sys.stdout.write('\rTweets collected: %s -- database size: %s kb' %
                                (db.entry_count,
                                 os.path.getsize(DATABASE_PATH) >> 10))
            sys.stdout.flush()

        except Exception, e:
            raise

    def on_error(self, error):
        pass


def collect():
    listener = CollectListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    stream = Stream(auth, listener)
    stream.filter(track=['Ferguson'])


if __name__ == '__main__':
    try:
        collect()
    except KeyboardInterrupt:
        print '\nDisconnecting from database...'
        db.disconnect_db()
        print 'Done.'
