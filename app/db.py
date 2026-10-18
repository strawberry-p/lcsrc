import sqlite3 as sq3
DB_PATH = "data/parts.db"
COMPL_DB: list[tuple[int,str,str,list[str],list[str],list[str]]] = [ # (type_id,type_name,type_db,common_attrs,possible_attrs,subtypes)
    (0,"Resistors","resistors",["Resistance","Tolerance","MOV"],["TempCo","Vmax"],["Thick Film","Carbon Film","Metal Oxide Film"]),
    (1,"Resistor arrays","resistor_arrays",["Resistance","Tolerance","TempCo","Num"],[],[]),
    (2,"Capacitors","capacitors",["Capacitance","Tolerance","Vmax","is_polarized"],[],["Electrolytic","Ceramic","Tantalum"]),
    (3,"Headers","headers",["Pitch", "Rows","Gender","is_right_angle"],["is_female","PinLength","RowSpacing","is_circular"],["Header","WireToBoard"]),
    (4,"Power connectors","power_conn",[],["ID","OD","Voltage","Current","is_right_angle","Pitch"],["BarrelJack","JST"]),
    (5,"PC connectors","pc_conn",["Height","is_right_angle","Standard"],["M2Key"],["DIMM","SO-DIMM","PCIe M.2"]),
    (6,"Spring clamp connectors","spring_conn",["Voltage","Current","Pitch","GaugeSurface","AWG"],["SpecMount"],["Spring clamp connector","Spring clamp terminal block"]),
    (7,"Battery Holders","bat",["ConnType","BatteryType","MinTemp","MaxTemp"],[],[])
    (8,"USB connectors",["Num","Pins","Standard","SpecMount","is_right_angle","is_female"],[],["USB-A","Micro-B","USB-C"]),
    (9,"Other data connectors","data_conn",["Pins","Current","Standard","is_female"],[],["HDMI"])
    ]
# A lot of useful parameters aren't in the JLCSearch website table! 'json' provides them

def get_db() -> tuple[sq3.Connection,sq3.Cursor]:
    conn = sq3.connect(DB_PATH)
    conn.row_factory = sq3.Row
    return (conn,conn.cursor())
def init_main_db():
    conn,cur = get_db()
    cur.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS main USING fts5(id, mfr,type,subtype,subsubtype,sort_id,company,desc,package,pins,is_smd,stock,power,high_price,high_price_count,low_price,low_price_count,assembly,is_basic,json)
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

