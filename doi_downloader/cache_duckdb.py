import duckdb
import json
import time
import os
from datetime import datetime, timedelta

class Cache:
    def __init__(self, db_name, table_name):
        self.db_name = db_name
        self.table_name = table_name
        self._initialize_database(db_name, table_name)

    def _initialize_database(self, db_name, table_name):
        # if not os.path.isfile(db_name):
            self.create_cache_table(db_name, table_name)

    def create_cache_table(self, db_name, table_name):
        conn = duckdb.connect(db_name)
        conn.execute(f'''CREATE TABLE IF NOT EXISTS "{table_name}"
                        (key TEXT PRIMARY KEY, value JSON, timestamp TEXT)''')
        conn.close()

    def get_all_cache(self):
        conn = duckdb.connect(self.db_name)
        rows = conn.execute(f'''SELECT * FROM {self.table_name}''').fetchall()
        conn.close()
        return rows

    def get_cache(self, key, ttl=0):
        conn = duckdb.connect(self.db_name)
        row = conn.execute(f'''SELECT value, timestamp FROM {self.table_name} WHERE key = ?''', (key,)).fetchone()
        conn.close()

        if not row:
            return None

        if ttl <= 0:
            value, _ = row
            return json.loads(value)

        value, timestamp_str = row
        timestamp = datetime.fromisoformat(timestamp_str)
        current_time = datetime.utcnow()

        if (timestamp + timedelta(seconds=ttl)) >= current_time:
            return json.loads(value)
        else:
            return None

    def set_cache(self, key, value):
        conn = duckdb.connect(self.db_name)
        # Saving UTC timestamp
        timestamp = datetime.utcnow().isoformat()
        conn.execute(f'''INSERT OR REPLACE INTO {self.table_name} (key, value, timestamp) VALUES (?, ?, ?)''',
                     (key, json.dumps(value), timestamp))
        conn.close()

    def delete_cache(self, key):
        conn = duckdb.connect(self.db_name)
        conn.execute(f'''DELETE FROM {self.table_name} WHERE key = ?''', (key,))
        conn.close()

    def clear_cache(self):
        conn = duckdb.connect(self.db_name)
        conn.execute(f'''DELETE FROM {self.table_name}''')
        conn.close()

    def delete_expired_cache(self, ttl=3600):
        conn = duckdb.connect(self.db_name)
        current_time = datetime.utcnow()
        rows = conn.execute(f'''SELECT key, timestamp FROM {self.table_name}''').fetchall()

        for key, timestamp_str in rows:
            timestamp = datetime.fromisoformat(timestamp_str)
            if (timestamp + timedelta(seconds=ttl)) <= current_time:
                conn.execute(f'''DELETE FROM {self.table_name} WHERE key = ?''', (key,))

        conn.close()

    def search_json(self, search_key, search_value):
        """
        Search for entries in the {self.table_name} where the JSON object contains a specific key-value pair.
        
        :param search_key: The key in the JSON object to search for.
        :param search_value: The value to match for the given key.
        :return: List of matching rows.
        """
        conn = duckdb.connect(self.db_name)
        
        # Prepare JSON path for extraction
        json_path = f'$.{search_key}'
        
        # Execute query to search inside JSON
        query = f'''
            SELECT key, value, timestamp 
            FROM {self.table_name} 
            WHERE json_extract(value, ?) = ?
        '''
        
        rows = conn.execute(query, (json_path, json.dumps(search_value))).fetchall()
        conn.close()
    
        return rows

    def get_count_all(self):
        conn = duckdb.connect(self.db_name)
        count = conn.execute(f'''SELECT COUNT(*) FROM {self.table_name}''').fetchone()[0]
        conn.close()
        return count

