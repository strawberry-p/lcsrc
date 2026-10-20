import requests as r
from pathlib import Path
import sys, time, csv
import app.db as db

METADATA_PATH = Path("data/meta.csv")
JLCP_CSV_PATH = Path("data/jlcpcb-components-basic-preferred.csv")
JLCP_DB_PATH = Path("data/jlcpcb-components.sqlite3")
JLCP_CSV_SOURCE = "https://cdfer.github.io/jlcpcb-parts-database/jlcpcb-components-basic-preferred.csv"
JLCP_DB_SOURCE = "https://cdfer.github.io/jlcpcb-parts-database/jlcpcb-components.sqlite3"
loaded_meta = {}
meta = {}
def main():
    global loaded_meta, meta
    if METADATA_PATH.is_file():
        with METADATA_PATH.open() as f:
            for line in f:
                if len(line) < 3 or ',' not in line: print(f"meta err: '{line}'")
                else:
                    a = line.split(",")
                    if a[0][0] == 'i': loaded_meta[a[0]] = int(a[1].strip())
                    elif a[0][0] == 'f': loaded_meta[a[0]] = float(a[1].strip())
                    elif a[0][0] == 'p': loaded_meta[a[0]] = Path(a[1].strip())
                    else: loaded_meta[a[0]] = a[1].strip()
    for i in loaded_meta.keys():
        meta[i] = loaded_meta[i]
    timenow = round(time.time())
    if "icsv_download" not in loaded_meta.keys() or (timenow-loaded_meta["icsv_download"]) > 3600*24 or not JLCP_CSV_PATH.is_file():
        csv_req = r.get(JLCP_CSV_SOURCE)
        JLCP_CSV_PATH.write_text(csv_req.text,encoding="utf-8")
        meta["icsv_download"] = timenow
    if "idb_download" not in loaded_meta.keys() or (timenow-loaded_meta["idb_download"]) > 3600*24 or not JLCP_DB_PATH.is_file():
        db_req = r.get(JLCP_DB_SOURCE)
        JLCP_DB_PATH.write_text(db_req.text,encoding="utf-8")
        meta["idb_download"] = timenow
    pass
    with METADATA_PATH.open("w") as f:
        f.writelines([f"{i},{meta[i]}\n" for i in meta.keys()])
    with db.get_db() as obtain:
        conn: db.sqlite3.Connection = obtain
        cur: db.sqlite3.Cursor = conn.cursor()
        with JLCP_CSV_PATH.open(newline='') as f:
            warn_count = 0
            line_count = 0
            cr = csv.DictReader(f,delimiter=',',quotechar='"')
            res = []
            for line in cr:
                prices = line["price"].split(",")
                lp = (prices[0].split(":")[0].split("-")[0],prices[0].split(":")[1])
                hp = (line["Min Order Qty"],prices[-1].split(":")[1])
                #num_id = float(cr["lcsc"][1:])
                id = "C"+line["lcsc"]
                num_id = int(line["lcsc"])
                tup: tuple = (num_id, id, line["mfr"], line["manufacturer"], line["category"], line["subcategory"], line["description"], lp[1], lp[0], hp[1], hp[0], line["attributes"],line["datasheet"])
                print(f"processing {num_id}: {tup}")
                if line["mfr"] == "" or line["attributes"] == "":
                    print(f"\n\nWARN: {id} missing one of {(line['mfr'],line['attributes'])}; desc is {line['description']}\n\n")
                    warn_count += 1
                else:
                    res.append(tup)
            print(f"processed {line_count} lines with {warn_count} warns")
            cur.executemany("""INSERT OR REPLACE INTO main (num_id,id,mfr,company,j_category,j_subcat,desc,j_lowp,j_lowp_c,j_highp,j_highp_c,json,datasheet) VALUES
                    (?,?,?,?,?,?,?,?,?,?,?,?,?)""",res)
        conn.commit()

if __name__ == "__main__": main()
