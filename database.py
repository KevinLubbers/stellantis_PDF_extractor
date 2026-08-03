import sqlite3

class Database:
    def __init__(self, db_path):
        
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def commit(self):
        self.conn.commit()

    def save_model(self, model):
        self.cursor.execute("INSERT OR IGNORE INTO models (division_id, model_code, year) VALUES (:division_id, :model_code, :year)", model)
        self.commit()
        return self.cursor.lastrowid

    def save_division(self, division):
        self.cursor.execute("INSERT OR IGNORE INTO divisions (division_name) VALUES (:division_name)", {"division_name": division}) 
        self.commit()

    def save_option(self, option):
        self.cursor.execute("INSERT INTO options (model_id, option_code, invoice, msrp, effective_date) VALUES (:model_id, :option_code, :invoice, :msrp, :effective_date)", option)
        self.commit()

    def create_model_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                division_id INTEGER NOT NULL,
                model_code TEXT NOT NULL UNIQUE,
                year INTEGER NOT NULL,
                FOREIGN KEY (division_id) REFERENCES divisions (id)
            )
        """)
        self.commit()

    def create_division_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS divisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                division_name TEXT NOT NULL UNIQUE
            )
        """)
        self.commit()

    def create_options_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id INTEGER NOT NULL,
                option_code TEXT NOT NULL,
                invoice INTEGER NOT NULL,
                msrp INTEGER NOT NULL,
                effective_date TEXT NOT NULL,
                FOREIGN KEY (model_id) REFERENCES models (id)
            )
        """)
        self.commit()
