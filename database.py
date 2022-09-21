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

    def create_user(self, id, name) -> bool:
        with self.connection:
            try:
                # Пишу запросы через жопу и мне пох
                self.cursor.execute(f"INSERT INTO User (id, name) VALUES ({id}, '{name}');")
                return True
            except Exception as error:
                print(f'[Ошибка добавления пользователя в БД] {error}')
                return False
            finally:
                self.connection.commit()

    def get_user_list(self):
        with self.connection:
            self.cursor.execute(f"SELECT id FROM User")
            return self.cursor.fetchall()
