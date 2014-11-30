import os
import string
import argparse
from databasehandler import CollectionDatabase

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database/')

STOPWORDS = set([x.strip() for x in open(os.path.join(os.path.dirname(__file__),
                                              'stopwords')).read().split('\n')])

def wordFreq(db):
    words = {}
    tweets = db.get_all_tweet_text()
    for tweet in tweets:
        tweet = [word.lower().strip('\'\"-,.:;!?][)(}{|') for word in tweet[0].split()]
        for word in tweet:
            # Current word is a stopword
            if word in STOPWORDS:
                continue

            # Current word is a link
            elif word.startswith('http'):
                continue

            elif word in words:
                words[word] += 1

            else:
                words[word] = 1

    top = sorted(words, key=words.get, reverse=True)[:50]
    for word in top:
        print '%s : %s' % (word, words[word])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', help='Provide a database name.')

    args = parser.parse_args()

    if not args.database:
        args.database = raw_input('Please provide a database name: ')

    db = CollectionDatabase(os.path.join(DATABASE_PATH, args.database))

    wordFreq(db)

    db.disconnect_db()
