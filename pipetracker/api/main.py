from fastapi import FastAPI, Request
from loguru import logger
from pipetracker.api.routes import trace


app = FastAPI(title="pipetracker API", version="0.1.3")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and responses."""
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"{response.status_code} {request.url}")
    return response


@app.get("/health")
def health_check():
    """Simple health endpoint."""
    return {"status": "ok", "service": "pipetracker"}


# Register the /trace routes
app.include_router(trace.router)
