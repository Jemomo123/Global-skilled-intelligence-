import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.scheduler import start_scheduler
from app.api.health import router as health_router

# Setup unified application logging matrix
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GlobalApplicationMain")

app = FastAPI(
    title="Global Skilled Intelligence",
    description="Skilled trade intelligence & live discovery service"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the production API routing interfaces
app.include_router(health_router)

@app.on_event("startup")
def startup_event():
    logger.info("FastAPI Lifecycle: Initializing system startup routing...")
    # Clean handoff to the single background scheduler
    start_scheduler()
    logger.info("FastAPI Lifecycle: Startup sequence fully completed.")

@app.get("/")
def read_root():
    return {"status": "online", "framework": "Phase 2 Production Modular"}
