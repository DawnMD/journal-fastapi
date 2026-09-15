from typing import Annotated

from clerk_backend_api import (
    AuthenticateRequestOptions,
    authenticate_request,
)
from fastapi import Depends, HTTPException, Request, status

from app.settings import settings


def get_current_user(request: Request) -> str:
    auth = authenticate_request(
        request,
        AuthenticateRequestOptions(
            secret_key=settings.CLERK_SECRET_KEY,
            jwt_key=settings.CLERK_JWT_KEY,
            authorized_parties=["http://localhost:3000", "https://*.vercel.app"],
            accepts_token=["session_token"],
        ),
    )

    if not auth.is_signed_in:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    return auth.payload["sub"]  # type: ignore


CurrentUser = Annotated[str, Depends(get_current_user)]
