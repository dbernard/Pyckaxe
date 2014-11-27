import os
from databasehandler import CollectionDatabase

DATABASE_PATH = 'database/tweets.db'

db = CollectionDatabase(DATABASE_PATH)

STOPWORDS = set([x.strip() for x in open(os.path.join(os.path.dirname(__file__),
                                              'stopwords')).read().split('\n')])

def wordFreq():
    words = {}
    tweets = db.get_all_tweet_text()
    for tweet in tweets:
        tweet = [word.lower().strip('\'\"-,.:;!?][)(}{|') for word in tweet[0].split()]
        for word in tweet:
            if word in STOPWORDS:
                continue

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
    wordFreq()

    db.disconnect_db()
