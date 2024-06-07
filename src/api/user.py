from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

from database.orm import User
from database.repository import UserRepository
from schema.request import SignUpRequest, LogInRequest
from schema.response import UserSchema, JWTResponse
from service.user import UserService

router = APIRouter(prefix="/users")


@router.post("/sign-up", status_code=201)
def user_sign_up_handler(
        request: SignUpRequest,
        user_service: UserService = Depends(),
        user_repo: UserRepository = Depends(),
):
    # password -> hashing -> hashed_password
    hashed_password: str = user_service.hash_password(
        plain_password=request.password
    )

    # User(username, email, hashed_password)
    user: User = User.create(
        username=request.username,
        email=request.email,
        hashed_password=hashed_password
    )

    # user -> db save
    user: User = user_repo.save_user(user=user)

    # return user(id, username)
    return UserSchema.from_orm(user)

@router.post("/log-in", response_model=JWTResponse)
async def user_log_in_handler(
        request: LogInRequest,
        user_repo: UserRepository = Depends(),
        user_service: UserService = Depends(),
):
    # db read user
    user: User | None = user_repo.get_user_by_email(
        email=request.email
    )
    if not user:
        raise HTTPException(status_code=404, detail="User Not Found")

    # user.password, request.password -> bcrypt.checkpw
    verified: bool = user_service.verify_password(
        plain_password=request.password,
        hashed_password=user.password,
    )
    if not verified:
        raise HTTPException(status_code=401, detail="Not Authorized")

    # create, return jwt
    access_token: str = await user_service.create_jwt(email=user.email)
    return JWTResponse(access_token=access_token)


## 테스트
@router.get("/get-token/{email}")
async def get_token(email: str):
    token = await UserService.redis.get(email)
    if token:
        return {"token": token.decode('utf-8')}
    raise HTTPException(status_code=404, detail="Token not found")