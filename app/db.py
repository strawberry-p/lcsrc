import sqlite3 as sq3
DB_PATH = "data/parts.db"
COMPL_DB: list[tuple[int,str,str,list[str],list[str],list[str]]] = [ # (type_id,type_name,type_db,common_attrs,possible_attrs,subtypes)
    (0,"Resistors","resistors",["Resistance","Tolerance","MOV"],["TempCo","Vmax"],["Thick Film","Carbon Film","Metal Oxide Film"]),
    (1,"Resistor Arrays","resistor_arrays",["Resistance","Tolerance","TempCo","Num"],[],[]),
    (2,"Capacitors","capacitors",["Capacitance","Tolerance","Vmax","is_polarized"],[],["Electrolytic","Ceramic","Tantalum"])
    ]
def get_db() -> tuple[sq3.Connection,sq3.Cursor]:
    conn = sq3.connect(DB_PATH)
    conn.row_factory = sq3.Row
    return (conn,conn.cursor())
def init_main_db():
    conn,cur = get_db()
    cur.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS main USING fts5(id, mfr,type,subtype,subsubtype,sort_id,company,desc,package,pins,stock,power,high_price,high_price_count,low_price,low_price_count,assembly,is_basic,json)
        """)
    conn.commit()
    conn.close()

def init_compl_tables():
    remake = False
    with get_db() as conn,cur:
        for data in COMPL_DB:
            res_keys:str = ""
            for i in data[3]: res_keys += i+","
            for i in data[4]: res_keys += i+","
            res_keys = res_keys[:-1]
            print(res_keys)
            if remake: cur.execute(f"DROP TABLE {data[2]} IF EXISTS")
            cur.execute(f"CREATE VIRTUAL TABLE IF NOT EXISTS {data[2]} USING fts5({res_keys})") #f-strings because none of this is user input
        conn.commit()
        conn.close()

