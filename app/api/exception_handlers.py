import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from app.exceptions import AppError

logger = logging.getLogger(__name__)

async def app_error_handler(request: Request, exc: AppError):

    logger.error(
        "Application error",
        extra={
            "error_code": exc.error_code,
            "context": exc.context,
            "path": request.url.path,
        },
    )

    return JSONResponse(
        status_code=exc.http_status,
        content=exc.to_dict(),
    )
async def unexpected_error_handler(request: Request, exc: Exception):

    logger.exception("Unexpected error occurred")

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type": "InternalServerError",
                "code": "internal_error",
                "message": "Unexpected error occurred",
            }
        },
    )