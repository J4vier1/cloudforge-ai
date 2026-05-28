from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {
        "project": "CloudForge AI",
        "status": "running"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }