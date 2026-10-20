from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import app.db as db
app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"),name="static")
t = Jinja2Templates(directory="app/templates")
@app.get("/",response_class=HTMLResponse)
async def everything(req: Request, bom: str = ""):
    bom.replace("<","&lt;")
    bom.replace(">","&gt;")
    bom.replace("&","&amp;")
    if req.headers.get("HX-Request"):
        spl = [x.split(',') for x in bom.split('\n')]
        print(spl)
        pairlist = []
        res = ""
        price_total = 0
        for i in spl:
            if not i[0]: continue
            if str(i[0])[0] == "C": pairlist.append((1,i[0]))
            elif str(i[1])[0] == "C": pairlist.append((int(i[0]),i[1]))
        with db.get_db() as conn:
            cur = conn.cursor()
            for pair in pairlist:
                print(pair)
                cur.execute("SELECT mfr,j_lowp,j_lowp_c,j_highp,j_highp_c,datasheet,j_category FROM main WHERE id = ?",(pair[1],))
                queryres = cur.fetchone()
                if not queryres:
                    queryres = ["NOT FOUND", 0, 1, 0, 1,"",""]
                    mfr = "NOT FOUND"
                elif queryres[5] and queryres[5] != "" and queryres[5] != "None" and queryres[5] != None: mfr = f"<a href={queryres[5]}>{queryres[0]}</a>"
                else: mfr = queryres[0]
                print(mfr)
                print([x for x in queryres])
                price = 0
                ppu = 0
                if pair[0] >= queryres[2]:
                    price = pair[0]*queryres[1]
                    ppu = queryres[1]
                elif pair[0] >= queryres[4]:
                    price = pair[0]*queryres[3]
                    ppu = queryres[3]
                else:
                    price = queryres[4]*queryres[3]
                    ppu = queryres[3]
                price_total += price
                res += f"<tr><td>{pair[0]}</td> <td>{pair[1]}</td> <td>{mfr}</td> <td>{queryres[6]}</td> <td>{ppu}</td> <td>{price}</td> </tr>\n"
            res += f"<tr><td></td><td><b>Total:</b></td> <td></td> <td></td> <td></td> <td>{price_total}</td></tr>"
        return t.TemplateResponse(req,"results.html",{"parts":res})
    else: return t.TemplateResponse(req,"index.html",{})
