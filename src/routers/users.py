"""Authentication endpoints: register, login, token refresh."""

from fastapi import APIRouter, Depends, HTTPException, status

from auth.security import decode_refresh_token
from dependencies import get_user_service
from schemas.token import AccessToken, RefreshRequest, TokenPair
from schemas.user import UserRegister, UserLogin
from services.user import UserService

auth_router = APIRouter(tags=["auth"])


@auth_router.post(
    "/register",
    response_model=TokenPair,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new account",
)
def handle_register(
    payload: UserRegister,
    service: UserService = Depends(get_user_service),
):
    return service.register(payload)


@auth_router.post(
    "/login",
    response_model=TokenPair,
    summary="Log in and receive an access + refresh token pair",
)
def handle_login(
    payload: UserLogin,
    service: UserService = Depends(get_user_service),
):
    return service.login(username=payload.username, password=payload.password)


@auth_router.post(
    "/refresh",
    response_model=AccessToken,
    summary="Exchange a refresh token for a new access token",
)
def handle_refresh(
    payload: RefreshRequest,
    service: UserService = Depends(get_user_service),
):
    try:
        user_id = decode_refresh_token(payload.refresh_token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Confirm user still exists and is active
    user = service.get_by_id(user_id)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated.",
        )

    from auth.security import create_access_token
    return AccessToken(access_token=create_access_token(user_id))
"""User profile endpoints."""

from fastapi import APIRouter, Depends

from dependencies import get_current_user
from models.user import User
from schemas.user import UserPublic

users_router = APIRouter(tags=["users"])


@users_router.get(
    "/me",
    response_model=UserPublic,
    summary="Get the currently authenticated user's profile",
)
def handle_get_me(current_user: User = Depends(get_current_user)):
    return UserPublic.model_validate(current_user)
