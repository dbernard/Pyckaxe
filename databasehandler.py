import sqlite3
import threading
import Queue


class CollectionDatabaseError(Exception):
    pass


class CollectionDatabaseWriter(object):
    def __init__(self, db):
        self._close = threading.Event()
        self._db_path = db
        self.dataq = Queue.Queue()
        self.entry_count = 0
        self._data_thread = self._start_thread()

    def _start_thread(self):
        t = threading.Thread(target=self._check_for_data)
        t.start()
        return t

    def _check_for_data(self):
        conn, cursor = self.connect_db(self._db_path)
        while not self._close.isSet():
            # Add tweet data to our database. Error if we can't save a tweet
            try:
                data = self.dataq.get(timeout=1)
                self.dataq.task_done()
                cursor.execute('INSERT INTO tweets VALUES (?, ?, ?, ?)', data)
                conn.commit()
                self.entry_count += 1

            except Queue.Empty:
                pass

            except sqlite3.Error, e:
                msg = 'Error saving tweet to database: %s' % str(e)
                raise CollectionDatabaseError(msg)

        conn.commit()
        conn.close()

    def connect_db(self, name):
        # Create the database if it does not exist
        conn = sqlite3.connect(name)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS tweets (
                                id INTEGER,
                                text TEXT,
                                created_at TEXT,
                                coords TEXT)''')
        conn.commit()

        return conn, cursor

    def disconnect_db(self):
        self.dataq.join()
        self._close.set()
        if self._data_thread.is_alive():
            self._data_thread.join()

    def add(self, data):
        self.dataq.put(data)


#TODO: Make sure the below works.
class CollectionDatabaseReader(object):
    def __init__(self, db):
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


