import os
import string
import argparse
from databasehandler import CollectionDatabaseReader

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database/')

STOPWORDS = set([x.strip() for x in open(os.path.join(os.path.dirname(__file__),
                                              'stopwords')).read().split('\n')])


class WordFreq(object):
    def __init__(self):
        self.words = {}

    def add_data(self, data):
        tweet = [word.lower().strip('\'\"-,.:;!?][)(}{|') for word in
                                                                data.split()]
        for word in tweet:
            # Current word is a stopword
            if word in STOPWORDS:
                continue

            # Current word is a link
            elif word.startswith('http') or word.startswith('www'):
                continue

            elif word in self.words:
                self.words[word] += 1

            else:
                self.words[word] = 1

    def get_results(self, n):
        top = sorted(self.words, key=self.words.get, reverse=True)[:n]
        result = []
        for word in top:
            result.append((word, self.words[word]))

        return result

    def graph_results(self, n):
        results = self.get_results(n)
        # TODO: Graphing stuff here.


def getWordFreq(db, n):
    wf = WordFreq()
    tweets = db.get_all_tweet_text()
    for tweet in tweets:
        wf.add_data(tweet[0])

    return wf.get_results(n)


if __name__ == '__main__':
    # python word_freq.py (number-of-results) --database=(databasename)
    parser = argparse.ArgumentParser()
    parser.add_argument('number', help='Get the top n terms.')
    parser.add_argument('--database', help='Provide a database name.')

    args = parser.parse_args()

    if not args.database:
        args.database = raw_input('Please provide a database name: ')

    try:
        args.number = int(args.number)
    except ValueError:
        print 'Argument "number" must be an integer.'

    db = CollectionDatabaseReader(os.path.join(DATABASE_PATH, args.database))

    results = getWordFreq(db, args.number)

    for result in results:
        print '%s - %s' % result

    db.disconnect_db()
