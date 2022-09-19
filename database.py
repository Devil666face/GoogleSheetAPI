import sqlite3
import os
import shutil
from pathlib import Path

class Database:
    def __init__(self, db_file_name='database.db') -> None:
        self.db = db_file_name
        self.connection = sqlite3.connect(self.db)
        self.cursor = self.connection.cursor()

    def get_last_record(self):
        with self.connection:
            self.cursor.execute("SELECT value FROM RecordTag ORDER BY id DESC LIMIT 1")
            return self.cursor.fetchone()[0]

    def update_last_record(self, record_date):
        with self.connection:
            self.cursor.execute(f"INSERT INTO RecordTag (value) VALUES (?)",(record_date,))
            self.connection.commit()
