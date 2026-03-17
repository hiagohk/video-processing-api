from typing import Dict, Optional


class AppError(Exception):

    error_code: str = "internal_error"
    http_status: int = 500
    message: str = "An unexpected error occurred"

    def __init__(
        self,
        message: Optional[str] = None,
        *,
        context: Optional[Dict] = None,
    ):
        if message:
            self.message = message

        self.context = context or {}

        super().__init__(self.message)

    def to_dict(self):

        return {
            "error": {
                "type": self.__class__.__name__,
                "code": self.error_code,
                "message": self.message,
                "context": self.context,
            }
        }