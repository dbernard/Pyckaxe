import os
import argparse
import plotly.plotly as py
from auth import auth
from plotly.graph_objs import *
from databasehandler import CollectionDatabase

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database/')

POSITIVE_WORDS = set([x.lower().strip() for x in open(os.path.join(
                 os.path.dirname(__file__),
                 'sentiment-words/positive-words')).read().strip().split('\n')])

NEGATIVE_WORDS = set([x.lower().strip() for x in open(os.path.join(
                 os.path.dirname(__file__),
                 'sentiment-words/negative-words')).read().strip().split('\n')])

NEGATING_WORDS = set([x.lower().strip() for x in open(os.path.join(
                 os.path.dirname(__file__),
                 'sentiment-words/negating-words')).read().strip().split('\n')])

# Emoticons
POSITIVE_EMOTICONS = [":)", "(:", ":D", ":')", "(':"]
NEGATIVE_EMOTICONS = [":(", "):", "D:", ":|", ":'(", ")':", "-_-", ":S"]


def sentiment_stacked_bars(sentiment, fname, title):
    creds = auth('credentials.csv')

    plotly_username = creds['plotly_username']
    plotly_key = creds['plotly_api_key']

    py.sign_in(plotly_username, plotly_key)

    pos, neu, neg = sentiment

    trace1 = Bar(
            x = ['sentiment'],
            y = [pos],
            name = 'Positive Tweets')

    trace2 = Bar(
            x = ['sentiment'],
            y = [neg],
            name = 'Negative Tweets',
            marker = Marker(color='rgb(255, 0, 0)'))

    data = Data([trace1, trace2])
    layout = Layout(title=title, barmode='group')
    fig  = Figure(data=data, layout=layout)
    plot_url = py.plot(fig, filename=fname)
    py.image.save_as(fig, 'images/%s.png' % fname)

    return plot_url


def get_sentiment(db):
    positive, neutral, negative = 0, 0, 0
    tweets = db.get_all_tweet_text()
    pos, neu, neg = [], [], []

    for tweet in tweets:
        sentiment = 0
        # Pre-check for emoticons before we strip away punctuation
        if any(emo in tweet[0] for emo in POSITIVE_EMOTICONS):
            sentiment += 1
        if any(emo in tweet[0] for emo in NEGATIVE_EMOTICONS):
            sentiment -= 1

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
            if len(neu) < 100:
                neu.append(tweet)

    return positive, neutral, negative


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', help='Provide a database name.')
    parser.add_argument('--plotbars', help='Generate bar chart with name.')

    args = parser.parse_args()

    if not args.database:
        args.database = raw_input('Please provide a database name: ')

    db = CollectionDatabase(os.path.join(DATABASE_PATH, args.database))

    sentiment = get_sentiment(db)

    if args.plotbars:
        title = raw_input('Graph title: ')
        plot_url = sentiment_stacked_bars(sentiment, args.plotbars, title)
        print 'Sentiment plotted.\nURL: %s\nImage: %s' % (plot_url,
                                                'images/%s.png' % args.plotbars)
    else:
        print 'Positive: %s\nNeutral: %s\nNegative: %s\n' % sentiment

    db.disconnect_db()

