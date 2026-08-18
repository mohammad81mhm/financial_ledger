from rest_framework.exceptions import APIException


class ApplicationError(APIException):
    """Business rule violation that is not a field validation error."""

    status_code = 400
    default_code = "application_error"

    def __init__(self, detail, *, code=None) -> None:
        super().__init__(detail)
        if code is not None:
            self.default_code = code
