import duckdb
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
        conn = duckdb.connect(db_name)
        conn.execute('''CREATE TABLE IF NOT EXISTS cache
                        (key TEXT PRIMARY KEY, value JSON, expiry INTEGER)''')
        conn.close()

    def get_all_cache(self):
        conn = duckdb.connect(self.db_name)
        rows = conn.execute('SELECT * FROM cache').fetchall()
        conn.close()
        return rows

    def get_cache(self, key, expiration=False):
        conn = duckdb.connect(self.db_name)
        current_time = int(time.time())
        row = conn.execute('SELECT value, expiry FROM cache WHERE key = ?', (key,)).fetchone()
        conn.close()

        if row is not None:
            value, expiry = row
            if not expiration or expiry is None or expiry >= current_time:
                return json.loads(value)
        return None

    def set_cache(self, key, value, ttl=3600):
        conn = duckdb.connect(self.db_name)
        expiry = int(time.time() + ttl)
        conn.execute('INSERT OR REPLACE INTO cache (key, value, expiry) VALUES (?, ?, ?)',
                     (key, json.dumps(value), expiry))
        conn.close()

    def delete_cache(self, key):
        conn = duckdb.connect(self.db_name)
        conn.execute('DELETE FROM cache WHERE key = ?', (key,))
        conn.close()

    def clear_cache(self):
        conn = duckdb.connect(self.db_name)
        conn.execute('DELETE FROM cache')
        conn.close()

    def delete_expired_cache(self):
        conn = duckdb.connect(self.db_name)
        current_time = int(time.time())
        conn.execute('DELETE FROM cache WHERE expiry IS NOT NULL AND expiry <= ?', (current_time,))
        conn.close()

    def get_count_of_value(self, value):
        conn = duckdb.connect(self.db_name)
        json_dump = json.dumps(value)
        count = conn.execute('SELECT COUNT(*) FROM cache WHERE value = ?', (json_dump,)).fetchone()[0]
        conn.close()
        return count

    def get_count_all(self):
        conn = duckdb.connect(self.db_name)
        count = conn.execute('SELECT COUNT(*) FROM cache').fetchone()[0]
        conn.close()
        return count

