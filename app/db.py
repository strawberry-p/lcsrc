import sqlite3 as sq3
DB_PATH = "data/parts.db"
def get_db() -> tuple[sq3.Connection,sq3.Cursor]:
    conn = sq3.connect(DB_PATH)
    conn.row_factory = sq3.Row
    return (conn,conn.cursor())
def init_main_db():
    conn,cur = get_db()
