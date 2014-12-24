import os
import argparse
import plotly.plotly as py
from auth import auth
from plotly.graph_objs import *
from databasehandler import CollectionDatabaseReader

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


class SentimentAnalysis(object):
    def __init__(self):
        self.text = []

    def add_text(self, text):
        self.text.append(text)

    def _graph_sentiment(self, sentiment, fname, title):
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


    def get_sentiment(self, graph=False, fname='sentiment', title=None):
        positive, neutral, negative = 0, 0, 0
        # NOTE: The below arrays are only used to glance at what is being
        # tracked as pos/neg/neu
        pos, neu, neg = [], [], []

        for tweet in self.text:
            sentiment = 0
            # Pre-check for emoticons before we strip away punctuation
            if any(emo in tweet for emo in POSITIVE_EMOTICONS):
                sentiment += 1
            if any(emo in tweet for emo in NEGATIVE_EMOTICONS):
                sentiment -= 1

            text = [word.lower().strip('\'\"-,.:;!?][)(}{|') for word in tweet.split()]
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

        if graph:
            url = self._graph_sentiment((positive, neutral, negative), fname, title)
            return url

        else:
            return positive, neutral, negative


def analyzeSentiment(db, graph, fname='sentiment', title=None):
    sa = SentimentAnalysis()
    tweets = db.get_all_tweet_text()
    for tweet in tweets:
        sa.add_text(tweet[0])

    result = sa.get_sentiment(graph, fname, title)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', help='Provide a database name.')
    parser.add_argument('--plotbars', help='Generate bar chart with name.')

    args = parser.parse_args()

    if not args.database:
        args.database = raw_input('Please provide a database name: ')

    db = CollectionDatabaseReader(os.path.join(DATABASE_PATH, args.database))

    if args.plotbars:
        title = raw_input('Graph title: ')
        plot_url = analyzeSentiment(db, True, args.plotbars, title)
        print 'Sentiment plotted.\nURL: %s\nImage: %s' % (plot_url,
                                                'images/%s.png' % args.plotbars)
    else:
        sentiment = analyzeSentiment(db, False)
        print 'Positive: %s\nNeutral: %s\nNegative: %s\n' % sentiment

    db.disconnect_db()

