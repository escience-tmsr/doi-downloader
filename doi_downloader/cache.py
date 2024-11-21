import sqlite3
import json
import time
import os

class Cache:
    def __init__(self, db_name):
        self.db_name = db_name
        self._initialize_database(db_name)

    def _initialize_database(self, db_name):
        if not os.path.isfile(db_name):
            self.create_cache_table(db_name)

    def create_cache_table(self, db_name):
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS cache
                    (key TEXT PRIMARY KEY, value TEXT, expiry INTEGER)''')
        conn.commit()
        conn.close()

    def get_all_cache(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('SELECT * FROM cache')
        rows = c.fetchall()
        conn.close()
        return rows

    def get_cache(self, key, expiration=False):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        current_time = int(time.time())
        c.execute('SELECT value, expiry FROM cache WHERE key = ?', (key,))
        row = c.fetchone()
        conn.close()
        if row is not None:
            value, expiry = row
            if not expiration:
                return json.loads(value)
            else:
                if expiry is None or expiry >= current_time:
                    return json.loads(value)
        return None

    def set_cache(self, key, value, ttl=3600):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        expiry = int(time.time() + ttl)
        c.execute('INSERT OR REPLACE INTO cache (key, value, expiry) VALUES (?, ?, ?)',
                (key, json.dumps(value), expiry))
        conn.commit()
        conn.close()

    def delete_cache(self, key):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('DELETE FROM cache WHERE key = ?', (key,))
        conn.commit()
        conn.close()

    def clear_cache(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('DELETE FROM cache')
        conn.commit()
        conn.close()

    def delete_expired_cache(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        current_time = int(time.time())
        c.execute('DELETE FROM cache WHERE expiry IS NOT NULL AND expiry <= ?', (current_time,))
        conn.commit()
        conn.close()

    def get_count_of_value(self, value):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        json_dump = json.dumps(value)
        c.execute('SELECT COUNT(*) FROM cache WHERE value = ?', (json_dump,))
        row = c.fetchone()
        conn.close()
        return row[0]

    def get_count_all(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM cache')
        row = c.fetchone()
        conn.close()
        return row[0]
