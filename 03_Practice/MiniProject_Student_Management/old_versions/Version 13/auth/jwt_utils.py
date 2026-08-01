"""
Day 015 Exercises 2 & 3: JWT Generation and Decoding with python-jose.
Day 019 Exercise 4: JWT secret and algorithm moved to .env / config.py.

This module demonstrates:
  - Exercise 2: Generating a signed JWT containing username, role, and expiration.
  - Exercise 3: Decoding a JWT to inspect its Header, Payload, and Signature.

What is a JWT?
--------------
A JSON Web Token (JWT) is a compact, URL-safe means of representing claims to
be transferred between two parties. A JWT has three Base64Url-encoded parts
separated by dots:

    <Header>.<Payload>.<Signature>

1. Header   : Metadata about the token (algorithm used, token type).
              Example: { "alg": "HS256", "typ": "JWT" }

2. Payload  : The claims (statements about an entity and additional data).
              Reserved claims: "sub" (subject), "exp" (expiration), "iat" (issued-at).
              Custom claims: "username", "role".
              Example: { "sub": "john_doe", "role": "admin", "exp": 1720000000 }

3. Signature: HMAC-SHA256(base64url(header) + "." + base64url(payload), SECRET_KEY)
              This guarantees the token has NOT been tampered with.

Why HS256?
----------
HS256 (HMAC + SHA-256) uses a single symmetric secret key for both signing and
verification — ideal for server-to-server scenarios where both the token issuer
and verifier are the same application. For cross-service or third-party scenarios,
RS256 (asymmetric RSA) would be preferred.

Security Note:
--------------
In production, SECRET_KEY must be a long, randomly-generated value stored in
environment variables or a secrets manager — NEVER hardcoded in source code.
"""

from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from jose.utils import base64url_decode
import json
import base64

# Day 019 Exercise 4: Read JWT configuration from .env via settings (not hardcoded).
# The old hardcoded SECRET_KEY is replaced by settings.jwt_secret_key.
from config import settings

# -----------------------------------------------------------------------
# Day 019 Exercise 4: JWT Configuration from Settings
# -----------------------------------------------------------------------
# These module-level names are kept for readability inside this file.
# They are read once at import time from the centralized settings object.
SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt_access_token_expire_minutes


# -----------------------------------------------------------------------
# Exercise 2: JWT Generation
# -----------------------------------------------------------------------

def create_access_token(username: str, role: str) -> str:
    """
    Exercise 2: Generate a signed JWT token with username, role, and expiration.

    How it works:
    -------------
    1. We build a `payload` dict with:
       - "sub"      (subject)    : Identifies the principal (the username).
       - "username"              : Redundant but explicit claim for easy extraction.
       - "role"                  : Custom claim declaring the user's access level.
       - "exp"      (expiration) : UTC timestamp after which this token is invalid.
       - "iat"      (issued-at)  : UTC timestamp of when the token was created.
    2. python-jose serializes + Base64Url-encodes the header and payload.
    3. It computes HMAC-SHA256 over "<encoded_header>.<encoded_payload>" using SECRET_KEY.
    4. The three parts are joined with dots into the final JWT string.

    Args:
        username (str): The authenticated user's username to embed in the token.
        role     (str): The user's role (e.g., "admin", "student", "teacher").

    Returns:
        str: A signed JWT string in the format: <header>.<payload>.<signature>
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": username,           # Standard claim: identifies the subject
        "username": username,      # Custom claim: explicit username field
        "role": role,              # Custom claim: user's role/permission level
        "exp": expire,             # Standard claim: token expiry (auto-handled by jose)
        "iat": now,                # Standard claim: issued-at timestamp
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


# -----------------------------------------------------------------------
# Exercise 3: JWT Decoding & Inspection
# -----------------------------------------------------------------------

def decode_token(token: str) -> dict:
    """
    Exercise 3: Decode and verify a JWT, returning its full payload.

    How it works:
    --------------
    1. python-jose splits the token at the dots into [header_b64, payload_b64, sig_b64].
    2. It re-computes the expected signature using SECRET_KEY and compares
       it against sig_b64 (using constant-time comparison to prevent timing attacks).
    3. If the signature is valid, it decodes and returns the payload dict.
    4. It also checks that "exp" > current UTC time — if expired, raises JWTError.

    Args:
        token (str): The raw JWT string to decode and verify.

    Returns:
        dict: The decoded and validated payload claims.

    Raises:
        JWTError: If the token is invalid, expired, or tampered with.
    """
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload


def inspect_token_parts(token: str) -> dict:
    """
    Decode a JWT's three structural parts without verifying the signature.

    This is intended for learning/debugging only. A token can be readable here
    while still being invalid for authentication if the signature or expiry fails.
    """
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid JWT format. Expected three parts separated by dots.")

    header_b64, payload_b64, signature_b64 = parts

    try:
        header = json.loads(base64url_decode(header_b64.encode("utf-8")))
        payload = json.loads(base64url_decode(payload_b64.encode("utf-8")))
        signature_bytes = base64url_decode(signature_b64.encode("utf-8"))
    except Exception as exc:
        raise ValueError("Invalid JWT encoding. Could not decode token parts.") from exc

    return {
        "header": header,
        "payload": payload,
        "signature_base64url": signature_b64,
        "signature_hex": signature_bytes.hex(),
        "note": "Signature is decoded for inspection only; it is not verified here.",
    }
