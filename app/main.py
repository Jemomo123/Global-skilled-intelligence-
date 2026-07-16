from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# 1. This tells FastAPI to serve your CSS/JS files from the "app/static" folder
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

# Mock data for your feed
JOBS_DATA = [
    {
        "title": "Red Seal Plumber",
        "company": "Global Skilled Industries",
        "location": "Toronto, ON",
        "description": "Looking for an experienced Journeyman Plumber for commercial projects.",
        "api_score": "100/100",
        "cv_match": True,
        "visa_sponsored": True,
        "work_permit": True,
        "relocation": True
    }
]

@app.get("/")
def read_dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")

@app.get("/api/jobs")
def get_jobs():
    return JOBS_DATA
