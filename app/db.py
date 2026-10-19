import sqlite3 as sq3
import json, sys
from pathlib import Path
DB_PATH = "data/parts.db"
CONFIG_PATH = Path("app/config.json")
COMPL_DB_ARRAY: list[list[str,str,list[str],list[str],list[str]]] = [] # (type_name,type_db,common_attrs,possible_attrs,subtypes)
# A lot of useful parameters aren't in the JLCSearch website table! 'json' provides them
CONFIG: dict = {}
dryrun: bool = False
remake: bool = False
remake_fts: bool = False

def get_db() -> tuple[sq3.Connection,sq3.Cursor]:
    conn = sq3.connect(DB_PATH)
    conn.row_factory = sq3.Row
    return (conn,conn.cursor())
def init_main_db():
    with get_db() as conn,cur:
        if remake_fts or remake:
            cur.execute("DROP TRIGGER IF EXISTS main_ins")
            cur.execute("DROP TRIGGER IF EXISTS main_del")
            cur.execute("DROP TRIGGER IF EXISTS main_upd")
            cur.execute("DROP TABLE IF EXISTS fts_main")
        if remake: cur.execute("DROP TABLE IF EXISTS main")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS main (num_id INTEGER PRIMARY KEY, id TEXT UNIQUE, mfr TEXT UNIQUE, type TEXT, subtype TEXT, type_index INT, j_category TEXT NOT NULL, j_subcat TEXT NOT NULL, sort_id INTEGER, company TEXT NOT NULL, company_id INT NOT NULL, desc TEXT, package TEXT, pins INTEGER, is_smd INTEGER, stock INTEGER, power REAL,
            j_highp REAL NOT NULL, j_highp_c INTEGER NOT NULL, j_lowp REAL NOT NULL, j_lowp_c INTEGER NOT NULL, l_highp REAL, l_highp_c INTEGER, l_lowp REAL, l_lowp_c INTEGER,
            assembly TEXT, is_basic INTEGER, is_preferred INTEGER, json TEXT NOT NULL)
            """)
        cur.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS fts_main USING fts5(id, mfr,company,desc,package,assembly,content='main',content_rowid='num_id')
            """)
        # j* = jlcpcb, l* = lcsc, p = price, p_c = min count for prize
        conn.commit()
        cur.execute("""CREATE TRIGGER IF NOT EXISTS main_ins AFTER INSERT ON main BEGIN
            INSERT INTO fts_main (rowid,id,mfr,company,desc,package,assembly) VALUES (new.num_id,new.id,new.mfr,new.company,new.desc,new.package,new.assembly); END;""")
        cur.execute("""CREATE TRIGGER IF NOT EXISTS main_del AFTER DELETE ON main BEGIN
            INSERT INTO fts_main (fts_main,rowid,id,mfr,company,desc,package,assembly) VALUES ('delete',old.num_id,old.id,old.mfr,old.company,old.desc,old.package,old.assembly); END;""")
        cur.execute("""CREATE TRIGGER IF NOT EXISTS main_upd AFTER UPDATE ON main BEGIN
            INSERT INTO fts_main (fts_main,rowid,id,mfr,company,desc,package,assembly) VALUES ('delete',old.num_id,old.id,old.mfr,old.company,old.desc,old.package,old.assembly);
            INSERT INTO fts_main (rowid,id,mfr,company,desc,package,assembly) VALUES (new.num_id,new.id,new.mfr,new.company,new.desc,new.package,new.assembly); END;""")
        conn.commit()
        conn.close()

def init_compl_tables():
    global COMPL_DB_ARRAY,CONFIG
    with get_db() as conn,cur:
        for data in COMPL_DB_ARRAY:
            res_keys:str = ""
            for i in data[3]: res_keys += i+","
            for i in data[4]: res_keys += i+","
            res_keys = res_keys[:-1]
            print(res_keys)
            if remake: cur.execute(f"DROP TABLE {data[2]} IF EXISTS")
            cur.execute(f"CREATE VIRTUAL TABLE IF NOT EXISTS {data[2]} USING fts5({res_keys})") #f-strings because none of this is user input
        conn.commit()
        conn.close()

if __name__ == "__main__":
    with CONFIG_PATH.open() as f:
        CONFIG = json.load(f)
    COMPL_DB_ARRAY = CONFIG["compl_db_array"]
    if "--dry-run" in sys.argv: dryrun = True
    if "--list-tables" in sys.argv:
        dryrun = True
        with get_db() as conn,cur:
            cur.execute("SELECT * FROM sqlite_master")
            print(cur.fetchall())
    if "--remake" in sys.argv:
        if !dryrun and input("delete and recreate empty tables? yes/*\n") == "yes": remake = True
    if "--remake-fts": remake_fts = True
    if "--compl" in sys.argv: init_compl_tables()
    init_main_db()
    with get_db() as conn,cur:
        if "--show-data" in sys.argv:
            cur.execute("SELECT id, mfr, company, package FROM main")
            out = ""
            i = 0
            for entry in cur.fetchmany(100):
                if out == "": out = f"{i}    {entry[0]} | {entry[1]} | {entry[2]} | {entry[3]}"
                else:
                    out += f"  ||  {entry[0]} | {entry[1]} | {entry[2]} | {entry[3]}"
                    print(out)
                    out = ""
                i += 1
        cur.execute("SELECT COUNT(id) FROM main")
        print(cur.fetchone())


