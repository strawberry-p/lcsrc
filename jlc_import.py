import requests as r
from pathlib import Path
import bs4, sys, time
import app.db

METADATA_PATH = Path("data/meta.csv")
JLCP_CSV_PATH = Path("data/jlcpcb-components-basic-preferred.csv")
JLCP_DB_PATH = Path("data/jlcpcb-components.sqlite3")
JLCP_CSV_SOURCE = "https://cdfer.github.io/jlcpcb-parts-database/jlcpcb-components-basic-preferred.csv"
JLCP_DB_SOURCE = "https://cdfer.github.io/jlcpcb-parts-database/jlcpcb-components.sqlite3"
loaded_meta = {}
meta = {}
def main():
    global loaded_meta, meta
    with METADATA_PATH.open() as f:
        for line in f:
            if len(line) < 3 or ',' not in line: print(f"meta err: '{line}'")
            else:
                a = line.split(",")
                if a[0][0] == 'i': loaded_meta[a[0]] = int(a[1])
                elif a[0][0] == 'f': loaded_meta[a[0]] = float(a[1])
                elif a[0][0] == 'p': loaded_meta[a[0]] = Path(a[1])
                else: loaded_meta[a[0]] = a[1]
    for i in loaded_meta.keys():
        meta[i] = loaded_meta[i]
    timenow = time.time()
    if "icsv_download" not in loaded_meta.keys() or (timenow-loaded_meta["icsv_download"]) > 3600*24 or not JLCP_CSV_PATH.is_file():
        csv_req = r.get(JLCP_CSV_SOURCE)
        JLCP_CSV_PATH.write_text(str(csv_req.content))
        meta["icsv_download"] = timenow
    if "idb_download" not in loaded_meta.keys() or (timenow-loaded_meta["idb_download"]) > 3600*24 or not JLCP_DB_PATH.is_file():
        db_req = r.get(JLCP_DB_SOURCE)
        JLCP_DB_PATH.write_text(str(db_req.content))
        meta["idb_download"] = timenow
    pass
    with METADATA_PATH.open() as f:
        f.writelines([f"{i},{meta[i]}\n" for i in meta.keys()])
    with db.get_db() as obtain:
        conn: db.sqlite3.Connection = obtain[0]
        cur: db.sqlite3.Cursor = obtain[1]
        with JLCP_CSV_PATH.open(newline='') as f:
            with csv.reader(f,delimiter=',',quotechar='"') as cr:
                for line in cr:
                    prices = cr["price"].split(",")
                    lp = (prices[0].split(":")[0].split("-")[0],prices[0].split(":")[1])
                    cur.execute("INSERT OR REPLACE INTO main (id,num_id,company,j_category,j_subcat,desc,json)")
        for i in csvdata
        cur.execute()

if __name__ == "__main__": main()
