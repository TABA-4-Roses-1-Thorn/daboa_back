from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from service.user import UserService

user_service = UserService()

async def auth_middleware(request: Request, call_next):
    token = request.headers.get("Authorization")
    if token:
        token = token.split("Bearer ")[-1]
        try:
            payload = user_service.decode_jwt(token)
            request.state.user_id = payload.get("sub")
        except HTTPException:
            pass  # Token validation failed
    response = await call_next(request)
    return response

async def session_middleware(request: Request, call_next):
    session_id = request.cookies.get("session")
    if session_id:
        request.state.user_id = int(session_id)
    else:
        request.state.user_id = None
    response = await call_next(request)
    return response