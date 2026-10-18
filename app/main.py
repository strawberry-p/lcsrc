from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
app = FastAPI()
t = Jinja2Templates(directory="app/templates")
@app.get("/",response_class=HTMLResponse)
async def everything(req: Request, bom: str = ""):
    bom.replace("<","&lt;")
    bom.replace(">","&gt;")
    bom.replace("&","&amp;")
    if req.headers.get("HX-Request"):
        return t.TemplateResponse(req,"results.html",{"parts":'\n'.join([f"<li>{x}</li>" for x in bom.strip().split("\n")])})
    else: return t.TemplateResponse(req,"index.html",{})
