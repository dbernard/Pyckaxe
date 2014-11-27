import os
import random
import argparse
from databasehandler import CollectionDatabase
from wordcloud import WordCloud

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database/')

STOPWORDS = set([x.strip() for x in open(os.path.join(os.path.dirname(__file__),
                                              'stopwords')).read().split('\n')])

def monochrome_color_func(word, font_size, position, orientation,
        random_state=None):
    if not random_state:
        random_state = Random()
    return 'hsl(0, 0%%, %d%%)' % random_state.randint(0, 50)

def get_word_cloud(db, image):
    text = generate_text(db)
    wc = WordCloud(width=1280, height=1024, stopwords=STOPWORDS,
                   background_color='white', color_func=monochrome_color_func,
                   max_words=100)

    wc.generate(text)
    wc.to_file(image)

def generate_text(db):
    text = []
    tweets = db.get_all_tweet_text()
    for tweet in tweets:
        text.append(tweet[0])

    text = ' '.join(text)

    return text


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', help='Provide a database name.')
    parser.add_argument('--name', help='Filename for the wordcloud png.')

    args = parser.parse_args()

    if not args.database:
        args.database = raw_input('Please provide a database name: ')

    if not args.name:
        name = raw_input('Please provide an image name: ')
        if not name.endswith('.png'):
            name += '.png'
        name = 'images/%s' % name
        args.name = name

    db = CollectionDatabase(os.path.join(DATABASE_PATH, args.database))
    image_path = os.path.join(os.path.dirname(__file__), args.name)
    print image_path

    print 'Generating word cloud...'
    get_word_cloud(db, image_path)

    db.disconnect_db()
    print 'Done. Image saved to %s.' % image_path
