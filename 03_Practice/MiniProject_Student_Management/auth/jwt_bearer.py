"""
Exercise 4: JWT Bearer Dependency — Protecting Endpoints.

This module provides a reusable FastAPI dependency that extracts and validates
a JWT from the `Authorization: Bearer <token>` header on every protected request.

How the OAuth2 Bearer Flow Works:
----------------------------------
1. Client POSTs credentials to `/auth/login` → server returns a JWT.
2. Client stores the JWT and includes it in subsequent requests:
       Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
3. For every protected endpoint, this dependency:
   a. Extracts the token from the Authorization header.
   b. Decodes and verifies the JWT signature using SECRET_KEY.
   c. Checks the `exp` claim — rejects expired tokens with HTTP 401.
   d. Returns the decoded payload so the path function can use user claims.

Why use OAuth2PasswordBearer?
------------------------------
FastAPI's `OAuth2PasswordBearer` does two things:
1. Tells the OpenAPI schema (Swagger UI) that this endpoint requires Bearer auth,
   enabling the "Authorize" button in /docs.
2. Automatically extracts the token from the Authorization header and raises
   HTTP 401 with `WWW-Authenticate: Bearer` if the header is missing.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from auth.jwt_utils import decode_token
from logger_config import get_logger

logger = get_logger(__name__)


# OAuth2PasswordBearer tells FastAPI that:
#   - The token is obtained from the endpoint at `tokenUrl`
#   - Incoming requests should carry the token in the Authorization: Bearer header
# Swagger UI reads this to show the "Authorize" padlock button.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Exercise 4: FastAPI dependency that validates the JWT and returns current user claims.

    This function is injected into any protected endpoint via `Depends(get_current_user)`.
    FastAPI calls it automatically before executing the path operation.

    Validation steps performed:
    ---------------------------
    1. `oauth2_scheme` extracts the raw token string from the Authorization header.
       If the header is missing, FastAPI raises HTTP 401 automatically.
    2. `decode_token()` verifies the HMAC-SHA256 signature — if the token was
       tampered with or signed with a different key, JWTError is raised.
    3. `decode_token()` checks the `exp` claim — if the token is expired, JWTError is raised.
    4. We validate that the payload contains a `sub` claim (the username).
    5. If all checks pass, we return the payload dict containing username, role, etc.

    HTTP Error Responses:
    ----------------------
    - 401 Unauthorized: Missing Authorization header (handled by oauth2_scheme).
    - 401 Unauthorized: Invalid signature (tampered token).
    - 401 Unauthorized: Token expired.
    - 401 Unauthorized: Token missing required claims (e.g., no `sub` field).

    Args:
        token (str): Raw JWT string, automatically extracted from the Authorization header.

    Returns:
        dict: Decoded JWT payload containing user claims (username, role, exp, iat).

    Raises:
        HTTPException 401: If the token is invalid, expired, or malformed.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Token is invalid or expired.",
    )

    try:
        # Decode + verify signature + verify expiry
        payload = decode_token(token)

        # Ensure the token contains a subject claim
        username: str = payload.get("sub")
        if username is None:
            logger.warning("JWT Bearer: Token missing 'sub' claim — rejecting request.")
            raise credentials_exception

        logger.debug("JWT Bearer: Token validated successfully for username='%s'.", username)
        return payload  # Contains: sub, username, role, exp, iat

    except JWTError as exc:
        # Covers: invalid signature, expired token, malformed JWT structure
        logger.warning("JWT Bearer: Token validation failed — %s", str(exc))
        raise credentials_exception
