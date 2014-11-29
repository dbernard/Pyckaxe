import os
import argparse
from databasehandler import CollectionDatabase

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database/')

POSITIVE_WORDS = set([x.lower().strip() for x in open(os.path.join(
                        os.path.dirname(__file__),
                        'sentiment-words/positive-words')).read().split('\n')])

NEGATIVE_WORDS = set([x.lower().strip() for x in open(os.path.join(
                        os.path.dirname(__file__),
                        'sentiment-words/negative-words')).read().split('\n')])

NEGATING_WORDS = set([x.lower().strip() for x in open(os.path.join(
                        os.path.dirname(__file__),
                        'sentiment-words/negating-words')).read().split('\n')])


def _sentiment_slider(tweets):
    pass

def get_sentiment(db):
    positive, neutral, negative = 0, 0, 0
    tweets = db.get_all_tweet_text()
    pos, neu, neg = [], [], []

    for tweet in tweets:
        sentiment = 0
        text = [word.lower().strip('\'\"-,.:;!?][)(}{|') for word in tweet[0].split()]
        # TODO: dont split, just search for pos/neg word in tweet, then
        # negating + pos/neg word in tweet
        # TODO: Look for emoticons!
        for i in xrange(len(text)):
            # Positive word and first word in tweet
            if text[i] in POSITIVE_WORDS and i == 0:
                sentiment += 1

            # Negative word and first word in tweet
            elif text[i] in NEGATIVE_WORDS and i == 0:
                sentiment -= 1

            # Negative word
            elif text[i] in NEGATIVE_WORDS:
                # Previous word is negating
                if text[i - 1] in NEGATING_WORDS:
                    sentiment += 1
                # Negative sentiment
                else:
                    sentiment -= 1

            # Positive word
            elif text[i] in POSITIVE_WORDS:
                # Previous word is negating
                if text[i - 1] in NEGATING_WORDS:
                    sentiment -= 1
                # Positive sentiment
                else:
                    sentiment += 1

        if sentiment > 0:
            positive += 1
            if len(pos) < 10:
                pos.append(tweet)
        elif sentiment < 0:
            negative += 1
            if len(neg) < 10:
                neg.append(tweet)
        else:
            neutral += 1
            if len(neu) < 10:
                neu.append(tweet)

    print 'Positive: %s\nNeutral: %s\nNegative: %s\n' % (positive, neutral, negative)
    print 'Pos:\n %s\nNeu:\n %s\nNeg:\n %s' % (pos, neu, neg)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', help='Provide a database name.')

    args = parser.parse_args()

    if not args.database:
        args.database = raw_input('Please provide a database name: ')

    db = CollectionDatabase(os.path.join(DATABASE_PATH, args.database))

    get_sentiment(db)

    db.disconnect_db()

