import fastapi as fa

from core.enums import ResponseDetailEnum


class UnauthorizedException(fa.HTTPException):
    def __init__(self):
        super().__init__(
            status_code=fa.status.HTTP_401_UNAUTHORIZED,
            detail=ResponseDetailEnum.unauthorized,
            headers={'WWW-Authenticate': 'Bearer'},
        )
