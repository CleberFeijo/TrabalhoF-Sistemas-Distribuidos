from fastapi import status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from ._base import ExceptionHandler

from ..models import RequestValidationErrorModel

__all__ = 'RequestValidationExcHandler',


class RequestValidationExcHandler(ExceptionHandler[RequestValidationError]):

    @classmethod
    def handler(cls, request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=RequestValidationErrorModel.from_request_validation_error(exc).model_dump(),
        )
