from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="./templates")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    # minimal static HTML page
    html = """
    <html>
      <head><title>DG Do Admin</title></head>
      <body>
        <h1>DG Do Admin Panel (placeholder)</h1>
        <p>Use API to interact with drivers and trips.</p>
      </body>
    </html>
    """
    return HTMLResponse(content=html)