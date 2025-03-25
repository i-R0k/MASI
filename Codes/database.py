import sqlite3

DB_NAME = "uniterms.db"

class DatabaseManager:
    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        """Tworzy tabelę, jeśli jeszcze nie istnieje."""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS uniterm (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                description TEXT,
                sA TEXT,
                sOp TEXT,
                sB TEXT,
                sA2 TEXT,
                sOp2 TEXT,
                sB2 TEXT
            )
        """)
        conn.commit()
        conn.close()

    def insert_uniterm(self, name, description, sA, sOp, sB, sA2="", sOp2="", sB2=""):
        """Wstawia nowy rekord do bazy.
           Pola sA2, sOp2, sB2 są opcjonalne."""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("""
            INSERT INTO uniterm (name, description, sA, sOp, sB, sA2, sOp2, sB2)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, description, sA, sOp, sB, sA2, sOp2, sB2))
        conn.commit()
        conn.close()

    def delete_uniterm(self, record_id):
        """Usuwa rekord o danym id."""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM uniterm WHERE id=?", (record_id,))
        conn.commit()
        conn.close()

    def update_uniterm_name(self, record_id, new_name):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("UPDATE uniterm SET name=? WHERE id=?", (new_name, record_id))
        conn.commit()
        conn.close()

    def fetch_all_uniterms(self):
        """Pobiera wszystkie rekordy z tabeli uniterm.
           Teraz rekord zwraca (id, name, description, sOp) – dodatkowe pola możesz dodać w razie potrzeby."""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT id, name, description, sOp FROM uniterm ORDER BY id DESC")
        rows = c.fetchall()
        conn.close()
        return rows

    def fetch_uniterm_by_id(self, record_id):
        """Pobiera szczegółowe dane rekordu o podanym id."""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT name, description, sA, sOp, sB, sA2, sOp2, sB2 FROM uniterm WHERE id=?", (record_id,))
        row = c.fetchone()
        conn.close()
        return row
