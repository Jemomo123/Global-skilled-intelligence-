from fastapi import FastAPI

# Initialize the FastAPI application
app = FastAPI(
    title="Global Skilled Intelligence API",
    version="1.0.0",
    description="API for the skilled trade intelligence and discovery service"
)

@app.get("/")
def read_root():
    """
    Root endpoint to verify the API is online and running.
    """
    return {
        "status": "online",
        "message": "Welcome to the Global Skilled Intelligence API!"
    }
    
