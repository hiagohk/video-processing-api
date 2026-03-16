
from fastapi import FastAPI, Request
from app.api.routes.videos import router
from fastapi import FastAPI
from app.exceptions.base import AppError
from app.api.exception_handlers import (
    app_error_handler,
    unexpected_error_handler,
)
import uuid

app = FastAPI(title="Video Processing API")

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, unexpected_error_handler)

@app.middleware("http")
async def correlation_middleware(request: Request, call_next):
    request.state.correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = request.state.correlation_id
    return response

app.include_router(router)
