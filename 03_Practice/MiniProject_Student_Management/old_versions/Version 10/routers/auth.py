"""
Auth Router Module — Day 015: JWT Authentication Practice.

This router integrates all five exercises into a single cohesive flow:

  Exercise 1 : Password hashing (used inside /login)
  Exercise 2 : JWT generation   (token returned by /login)
  Exercise 3 : JWT decoding     (exposed via /auth/inspect-token)
  Exercise 4 : Protected endpoint GET /profile (requires valid JWT)
  Exercise 5 : Swagger testing  (all scenarios testable via /docs)

Endpoint Summary:
-----------------
POST /auth/login              — Authenticate with username + password, receive JWT.
GET  /auth/demo/hash          — Demo: hash a password and verify it (Exercise 1).
GET  /auth/demo/token         — Demo: generate and inspect a JWT (Exercises 2 & 3).
POST /auth/inspect-token      — Manually inspect any JWT's Header/Payload/Signature.
GET  /profile                 — Protected endpoint. Requires valid Bearer token.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from auth.password_utils import hash_password, verify_password
from auth.jwt_utils import create_access_token, decode_token, inspect_token_parts
from auth.jwt_bearer import get_current_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication — Day 015"],
)


# -----------------------------------------------------------------------
# Pydantic Schemas for Request/Response Bodies
# -----------------------------------------------------------------------

class TokenResponse(BaseModel):
    """Response model returned after successful authentication."""
    access_token: str
    token_type: str
    expires_in_minutes: int
    username: str
    role: str


class InspectTokenRequest(BaseModel):
    """Request model for manually inspecting a JWT."""
    token: str



# -----------------------------------------------------------------------
# Fake User Database (for demonstration only)
# -----------------------------------------------------------------------
# In a real application this would come from the PostgreSQL database.
# Passwords are stored as bcrypt hashes — NEVER as plain text.
#
# How these hashes were generated:
#   hash_password("admin123")   → $2b$12$...
#   hash_password("student456") → $2b$12$...
#
# We compute them at module load time here for demo clarity.
# -----------------------------------------------------------------------
FAKE_USERS_DB: dict[str, dict] = {
    "admin": {
        "username": "admin",
        "role": "admin",
        "hashed_password": hash_password("admin123"),
    },
    "alice": {
        "username": "alice",
        "role": "student",
        "hashed_password": hash_password("student456"),
    },
    "bob": {
        "username": "bob",
        "role": "teacher",
        "hashed_password": hash_password("teacher789"),
    },
}


# -----------------------------------------------------------------------
# Exercise 1 Demo: Password Hashing & Verification
# -----------------------------------------------------------------------

@router.get(
    "/demo/hash",
    summary="[Exercise 1] Demo: Password Hashing with passlib",
    description=(
        "Demonstrates bcrypt password hashing and verification using passlib. "
        "Hashes a sample password, then verifies it with a correct and wrong password."
    ),
    status_code=status.HTTP_200_OK,
)
def demo_password_hashing():
    """
    Exercise 1: Live demonstration of password hashing and verification.

    Shows:
    ------
    - A plain-text password being hashed (notice the $2b$ bcrypt prefix).
    - The same password verifying as True.
    - A wrong password verifying as False.
    - That hashing the same password twice produces DIFFERENT hashes (salt proof).
    """
    plain_password = "my_secret_password_123"

    # Hash the password (bcrypt with random salt each time)
    hashed1 = hash_password(plain_password)
    hashed2 = hash_password(plain_password)  # Different hash same password!

    # Below mentioned return statements are very descriptive just for test understanding purposes.
    # it doesn't have any interactive capabilities - it just shows that a random password is taken, hash generated few times and gets verified successfully.
    return {
        "exercise": "Exercise 1: Password Hashing",
        "plain_password": plain_password,
        "hashed_password_1": hashed1,
        "hashed_password_2_same_input": hashed2,
        "salt_proof": "Both hashes above are different — bcrypt uses a random salt each time!",
        "verification_results": {
            "correct_password_matches": verify_password(plain_password, hashed1),
            "wrong_password_matches": verify_password("wrong_password", hashed1),
        },
        "how_bcrypt_works": (
            "bcrypt hash format: $2b$<cost>$<22-char-salt><31-char-digest>. "
            "The cost factor (default 12) means 2^12 = 4096 iterations, making "
            "brute-force attacks computationally expensive."
        )
    }


# -----------------------------------------------------------------------
# Exercise 1 + 2: Login — Authenticate and Issue JWT
# -----------------------------------------------------------------------

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="[Exercise 1+2] Login — Authenticate & Receive JWT",
    description=(
        "Authenticate with username and password. If credentials are valid, "
        "a signed JWT containing username, role, and expiration is returned. "
        "Use this token as a Bearer token for protected endpoints. "
        "\n\n**Demo credentials:**\n"
        "- `admin` / `admin123` (role: admin)\n"
        "- `alice` / `student456` (role: student)\n"
        "- `bob` / `teacher789` (role: teacher)"
    ),
    status_code=status.HTTP_200_OK,
)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Exercise 1 + 2: Authenticate with username/password and issue a JWT.

    How it works:
    -------------
    1. Look up the user in our fake database by username.
    2. Use `verify_password()` (Exercise 1) to check the plain password
       against the stored bcrypt hash — this is constant-time comparison.
    3. If valid, use `create_access_token()` (Exercise 2) to generate a
       signed JWT containing username, role, and expiration claim.
    4. Return the JWT so the client can store it and use it in future requests.

    OAuth2PasswordRequestForm expects:
    -----------------------------------
    Form fields (not JSON): `username` and `password`.
    Swagger UI sends these as an HTML form when you click "Authorize".

    HTTP Error Responses:
    ----------------------
    - 401 Unauthorized: Unknown username.
    - 401 Unauthorized: Wrong password.
    """

    user = FAKE_USERS_DB.get(form_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Step 1: Verify password (Exercise 1 — bcrypt verification)
    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Step 2: Generate JWT (Exercise 2 — JWT creation)
    token = create_access_token(
        username=user["username"],
        role=user["role"]
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in_minutes=30,
        username=user["username"],
        role=user["role"],
    )


# -----------------------------------------------------------------------
# Exercise 2 + 3 Demo: Generate & Inspect a JWT
# -----------------------------------------------------------------------

@router.get(
    "/demo/token",
    summary="[Exercise 2+3] Demo: JWT Generation & Inspection",
    description=(
        "Generates a demo JWT and immediately decodes all three parts: "
        "Header, Payload, and Signature. Use this to visually understand "
        "the structure of a JWT without needing to log in."
    ),
    status_code=status.HTTP_200_OK,
)
def demo_jwt_generation_and_inspection():
    """
    Exercise 2 + 3: Generate a demo JWT and inspect all three parts.

    Shows:
    ------
    - The raw JWT string (the three base64url parts separated by dots).
    - Decoded Header: algorithm and token type.
    - Decoded Payload: username, role, expiration, issued-at.
    - Signature info: base64url and hex representation.
    """
    # Exercise 2: Generate token
    demo_token = create_access_token(username="demo_user", role="student")

    # Exercise 3: Decode token
    payload = decode_token(demo_token)
    parts = inspect_token_parts(demo_token)

    return {
        "exercise": "Exercise 2 + 3: JWT Generation & Inspection",
        "raw_jwt": demo_token,
        "jwt_structure_explanation": {
            "format": "<Header>.<Payload>.<Signature>",
            "encoding": "Each part is Base64Url-encoded",
            "separator": "The three parts are separated by dots '.'",
        },
        "decoded_header": parts["header"],
        "decoded_payload": payload,
        "signature": {
            "base64url": parts["signature_base64url"],
            "hex": parts["signature_hex"],
            "explanation": parts["note"],
        },
    }


# -----------------------------------------------------------------------
# Exercise 3: Inspect Any Token
# -----------------------------------------------------------------------

@router.post(
    "/inspect-token",
    summary="[Exercise 3] Inspect Token — Decode Header, Payload & Signature",
    description=(
        "Paste any JWT to decode and inspect its Header, Payload, and Signature. "
        "**Note:** This does NOT verify the signature — it only decodes the parts. "
        "For educational use. Try pasting an expired or invalid token here too!"
    ),
    status_code=status.HTTP_200_OK,
)
def inspect_token(request: InspectTokenRequest):
    """
    Exercise 3: Decode and visually inspect a JWT's three parts.

    This endpoint performs NO signature verification — it simply base64url-decodes
    each section, mirroring how jwt.io works. This lets you inspect expired or
    even tampered tokens for learning purposes.

    Use cases:
    ----------
    - Paste the token from /auth/login to see its contents.
    - Paste an expired token to see that the payload is still readable (but invalid).
    - Manually modify a token and paste it to see what happens to the structure.
    """
    try:
        parts = inspect_token_parts(request.token)
        return {
            "exercise": "Exercise 3: JWT Decoding",
            "decoded_header": parts["header"],
            "decoded_payload": parts["payload"],
            "signature": {
                "base64url": parts["signature_base64url"],
                "hex": parts["signature_hex"],
                "explanation": parts["note"],
            },
            "reminder": (
                "This endpoint does NOT verify the signature. "
                "Use GET /profile with the Authorization header to test full validation."
            )
        }
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )


# -----------------------------------------------------------------------
# Exercise 4: Protected Profile Endpoint
# -----------------------------------------------------------------------

@router.get(
    "/profile",
    summary="[Exercise 4+5] Protected — GET /profile (requires valid JWT)",
    description=(
        "**Protected endpoint.** Returns the current user's profile only if a **valid JWT** "
        "is provided in the `Authorization: Bearer <token>` header.\n\n"
        "**Exercise 5 — Swagger Testing Scenarios:**\n"
        "1. **No token** → Click 'Try it out' without authorizing → `401 Unauthorized`\n"
        "2. **Invalid token** → Authorize with `Bearer abc123` → `401 Unauthorized`\n"
        "3. **Expired token** → Use a token from >30 min ago → `401 Unauthorized`\n"
        "4. **Valid token** → Login via `/auth/login`, copy token, Authorize → `200 OK`"
    ),
    status_code=status.HTTP_200_OK,
    tags=["Authentication — Day 015"],
)
def get_profile(current_user: dict = Depends(get_current_user)):
    """
    Exercise 4: Protected endpoint — returns user profile data from JWT claims.

    The `Depends(get_current_user)` guard:
    --------------------------------------
    1. Extracts the Bearer token from the Authorization header.
    2. Verifies the JWT signature using the SECRET_KEY.
    3. Checks the token is not expired (`exp` claim).
    4. If all checks pass, injects the decoded payload as `current_user`.
    5. If any check fails, FastAPI raises HTTP 401 BEFORE this function runs.

    The path operation only executes if the user is authenticated.
    It reads claims directly from the verified JWT payload — no database call needed.
    This is the stateless nature of JWT: all user context is self-contained in the token.

    Exercise 5 Testing Scenarios (in Swagger /docs):
    -------------------------------------------------
    Scenario 1 — No token:
        → Do NOT click Authorize. Hit "Try it out" → Execute.
        → Response: 401 {"detail": "Not authenticated"}

    Scenario 2 — Invalid token:
        → Click Authorize. Enter: Bearer invalid_token_abc
        → Response: 401 {"detail": "Could not validate credentials..."}

    Scenario 3 — Expired token:
        → Use a JWT generated > 30 minutes ago.
        → Response: 401 {"detail": "Could not validate credentials..."}

    Scenario 4 — Valid token:
        → POST to /auth/login, copy the `access_token`.
        → Click Authorize. Enter: <paste token>
        → Response: 200 with full profile data.
    """
    # Extract claims from the verified JWT payload
    exp_timestamp = current_user.get("exp")
    iat_timestamp = current_user.get("iat")

    return {
        "message": "Access granted! You are authenticated.",
        "profile": {
            "username": current_user.get("username"),
            "role": current_user.get("role"),
            "subject": current_user.get("sub"),
        },
        "token_metadata": {
            "issued_at": (
                datetime.fromtimestamp(iat_timestamp, tz=timezone.utc).isoformat()
                if iat_timestamp else None
            ),
            "expires_at": (
                datetime.fromtimestamp(exp_timestamp, tz=timezone.utc).isoformat()
                if exp_timestamp else None
            ),
        },
        "access_level": {
            "admin": current_user.get("role") == "admin",
            "can_manage_students": current_user.get("role") in ["admin", "teacher"],
            "read_only": current_user.get("role") == "student",
        },
        "exercise_note": (
            "This data was extracted entirely from the JWT payload — "
            "no database call was made. This is the stateless advantage of JWT."
        )
    }
