# https://github.com/nsidnev/fastapi-realworld-example-app/blob/a5a4e73fbbfdbe2219d50209c5bb4727be99dcf2/app/api/errors/http_error.py
from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse


async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse({"errors": [exc.detail]}, status_code=exc.status_code)
