# pipetrack/api/main.py
from fastapi import FastAPI, Request
from loguru import logger

app = FastAPI(title="pipetrack API", version="0.1.0")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and responses."""
    logger.info(f"➡️ {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"⬅️ {response.status_code} {request.url}")
    return response


@app.get("/health")
def health_check():
    """Simple health endpoint."""
    return {"status": "ok", "service": "pipetrack"}
