import os
import random
from databasehandler import CollectionDatabase
from wordcloud import WordCloud

DATABASE_PATH = 'database/tweets.db'
IMAGE_PATH = os.path.join(os.path.dirname(__file__), 'wordcloud.png')

db = CollectionDatabase(DATABASE_PATH)

STOPWORDS = set([x.strip() for x in open(os.path.join(os.path.dirname(__file__),
                                              'stopwords')).read().split('\n')])

def monochrome_color_func(word, font_size, position, orientation,
        random_state=None):
    if not random_state:
        random_state = Random()
    return 'hsl(0, 0%%, %d%%)' % random_state.randint(0, 50)

def get_word_cloud():
    text = generate_text()
    wc = WordCloud(width=1280, height=1024, stopwords=STOPWORDS,
                   background_color='white', color_func=monochrome_color_func,
                   max_words=100)

    wc.generate(text)
    wc.to_file(IMAGE_PATH)

def generate_text():
    text = []
    tweets = db.get_all_tweet_text()
    for tweet in tweets:
        text.append(tweet[0])

    text = ' '.join(text)

    return text


if __name__ == '__main__':
    print 'Generating word cloud...'
    get_word_cloud()

    db.disconnect_db()
    print 'Done. Image saved to %s.' % IMAGE_PATH
