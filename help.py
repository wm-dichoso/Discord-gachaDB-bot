import logging
from dataclasses import dataclass
from typing import Any, Optional

logger = logging.getLogger(__name__)  

@dataclass
class Result:
    success: bool
    code: str
    message: str = ""
    data: Optional[Any] = None
    error: Optional[str] = None

    @classmethod
    def ok(cls, code: str, message: str = "", data: Any = None):
        return cls(
            success=True,
            code=code,
            message=message,
            data=data
        )

    @classmethod
    def fail(cls, code: str, message: str = "", error: str = None):
        logger.error(
            "Result.fail triggered | code=%s | message=%s | error=%s",
            code, message, error,
            exc_info=bool(error)
        )
        
        return cls(
            success=False,
            code=code,
            message=message,
            error=error
        )
