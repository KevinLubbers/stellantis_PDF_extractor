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

    def order_guide_exists(self, effective_date, model_id):
        self.cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM options WHERE effective_date = :effective_date AND model_id = :model_id)", {"effective_date": effective_date, "model_id": model_id}
        )
        return bool(self.cursor.fetchone()[0])
    def save_option(self, option):
        self.cursor.execute("INSERT INTO options (model_id, option_code, invoice, msrp, effective_date) VALUES (:model_id, :option_code, :invoice, :msrp, :effective_date)", option)
        self.commit()

    def create_model_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                division_id INTEGER NOT NULL,
                model_code TEXT NOT NULL,
                year INTEGER NOT NULL,
                FOREIGN KEY (division_id) REFERENCES divisions (id)
                UNIQUE (model_code, year)
            )
        """)
        self.commit()

    def get_or_create_model(self, division_id, model_code, year):
        self.cursor.execute(
            """
            SELECT id
            FROM models
            WHERE division_id = :division_id
            AND model_code = :model_code
            AND year = :year
            """,
            {
                "division_id": division_id,
                "model_code": model_code,
                "year": year,
            },
        )

        row = self.cursor.fetchone()

        if row:
            return row[0]

        self.cursor.execute(
            """
            INSERT INTO models (division_id, model_code, year)
            VALUES (:division_id, :model_code, :year)
            """,
            {
                "division_id": division_id,
                "model_code": model_code,
                "year": year,
            },
        )

        self.commit()
        return self.cursor.lastrowid

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
                FOREIGN KEY (model_id) REFERENCES models (id),
                UNIQUE (model_id, option_code, effective_date, invoice, msrp)
            )
        """)
        self.commit()

    def get_divisions(self):
        self.cursor.execute(
            "SELECT id, division_name FROM divisions ORDER BY division_name"
        )
        return self.cursor.fetchall()

    def get_menu_models(self):
        self.cursor.execute(
            "SELECT id, model_code, year FROM models ORDER BY model_code"
        )
        return self.cursor.fetchall()

    def get_dates_for_model(self, model_id):
        self.cursor.execute(
            "SELECT DISTINCT effective_date FROM options WHERE model_id = :model_id ORDER BY effective_date", {"model_id": model_id}
        )
        return [row[0] for row in self.cursor.fetchall()]

    def get_options_from_model_and_date(self, model_id, effective_date):
        self.cursor.execute(
            "SELECT option_code, invoice, msrp FROM options WHERE model_id = :model_id AND effective_date = :effective_date",
            {"model_id": model_id, "effective_date": effective_date},
        )
        return self.cursor.fetchall()