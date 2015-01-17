import os
import random
import argparse
from databasehandler import CollectionDatabaseReader
from wordcloud import WordCloud

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database/')

STOPWORDS = set([x.strip() for x in open(os.path.join(os.path.dirname(__file__),
                                              'stopwords')).read().split('\n')])

def monochrome_color_func(word, font_size, position, orientation,
        random_state=None):
    if not random_state:
        random_state = Random()
    return 'hsl(0, 0%%, %d%%)' % random_state.randint(0, 50)

def dark_monochrome_color_func(word, font_size, position, orientation,
                                    random_state=None):
    if not random_state:
        random_state = Random()
    return 'hsl(0, 0%%, %d%%)' % random_state.randint(40, 100)


class WordCloudBuilder(object):
    def __init__(self):
        self.text = []

    def add_data(self, data):
        # data should be a string
        self.text.append(data)

    def generate_wordcloud(self, filename, bg_color='white', stopwords=STOPWORDS,
                            color_func=monochrome_color_func, xtra_stopwords=[]):
        text = ' '.join(self.text)

        # These extra stopwords exist for cases where we want to ignore words
        # specific to one scenario - in other words, ignore words we may NOT
        # want to add to our base stopwords set or ignore normally.
        if xtra_stopwords:
            for word in xtra_stopwords:
                # stopwords is a set...
                if isinstance(stopwords, set):
                    stopwords.add(word)
                # Otherwise assume its a list
                else:
                    stopwords.append(word)

        wc = WordCloud(width=1280, height=1024, stopwords=stopwords,
                   background_color=bg_color, color_func=color_func,
                   max_words=100)

        wc.generate(text)
        wc.to_file(filename)


def createWordcloud(db, filename, bg_color='white', xtra_stopwords=[],
                                        color_func=monochrome_color_func):
    # TODO: make sure db is default listener derived
    wc = WordCloudBuilder()
    tweets = db.get_all_tweet_text()
    for tweet in tweets:
        wc.add_data(tweet[0])

    wc.generate_wordcloud(filename, bg_color=bg_color, color_func=color_func,
            xtra_stopwords=xtra_stopwords)


if __name__ == '__main__':
    # python word_cloud.py --name=(image-name) --database=(database-name)
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', help='Provide a database name.')
    parser.add_argument('--name', help='Filename for the wordcloud png.')
    parser.add_argument('--xtrastopwords', default=[],
                help='Ignore these words in addition to your default stopwords.'\
                        ' All words should be in one set of quotes and each '\
                        'word separated by a space.')
    parser.add_argument('--colorfunc', default='monochrome',
                help='Provide a color func: "monochrome" or "monochrome-dark"')

    args = parser.parse_args()

    if not args.database:
        args.database = raw_input('Please provide a database name: ')

    if not args.name:
        name = raw_input('Please provide an image name: ')
        if not name.endswith('.png'):
            name += '.png'
        name = 'images/%s' % name
        args.name = name

    if args.xtrastopwords:
        args.xtrastopwords = args.xtrastopwords.split(' ')

    if args.colorfunc not in ['monochrome', 'monochrome-dark']:
        args.colorfunc = 'monochrome'

    if args.colorfunc == 'monochrome':
        bg_color = 'white'
        args.colorfunc = monochrome_color_func
    else:
        bg_color = 'black'
        args.colorfunc = dark_monochrome_color_func

    db = CollectionDatabaseReader(os.path.join(DATABASE_PATH, args.database))
    image_path = os.path.join(os.path.dirname(__file__), args.name)

    print 'Generating word cloud...'
    createWordcloud(db, image_path, bg_color, args.xtrastopwords, args.colorfunc)

    db.disconnect_db()
    print 'Done. Image saved to %s.' % image_path
