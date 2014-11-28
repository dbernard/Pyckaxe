import sqlite3

class CollectionDatabaseError(Exception):
    pass

class CollectionDatabase(object):
    def __init__(self, db):
        self.entry_count = 0
        self.conn = None
        self.cursor = None
        self.connect_db(db)

    def connect_db(self, name):
        # Create the database if it does not exist
        self.conn = sqlite3.connect(name)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tweets (
                                id INTEGER,
                                text TEXT,
                                created_at TEXT,
                                coords TEXT)''')
        self.conn.commit()

    def disconnect_db(self):
        self.conn.commit()
        self.conn.close()

    def add(self, data):
        # Add tweet data to our database. Error if we can't save a tweet
        try:
            self.cursor.execute('INSERT INTO tweets VALUES (?, ?, ?, ?)', data)
            self.conn.commit()
            self.entry_count += 1
        except sqlite3.Error, e:
            msg = 'Error saving tweet to database: %s' % str(e)
            raise CollectionDatabaseError(msg)

    def get_all(self):
        try:
            self.cursor.execute('SELECT * FROM tweets')
            results = self.cursor.fetchall()
            return results
        except sqlite3.Error, e:
            msg = 'Error getting all tweets: %s' % str(e)
            raise CollectionDatabaseError(msg)

    def get_all_tweet_text(self):
        try:
            self.cursor.execute('SELECT text FROM tweets')
            text = self.cursor.fetchall()
            return text
        except sqlite3.Error, e:
            msg = 'Error getting all tweet text: %s' % str(e)
            raise CollectionDatabaseError(msg)


