
from fastapi import FastAPI, Request
from app.api.routes.videos import router
import uuid

app = FastAPI(title="Video Processing API")

@app.middleware("http")
async def correlation_middleware(request: Request, call_next):
    request.state.correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = request.state.correlation_id
    return response

app.include_router(router)
