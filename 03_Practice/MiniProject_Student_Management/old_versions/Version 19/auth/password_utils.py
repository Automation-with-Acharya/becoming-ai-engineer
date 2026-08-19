"""
Exercise 1: Password Hashing with passlib.

This module demonstrates how to securely hash passwords using the bcrypt algorithm
via the `passlib` library, and how to verify a plain-text password against a hash.

Why bcrypt?
-----------
- bcrypt is a *work-factor adaptive* hashing algorithm: as hardware gets faster,
  the cost parameter can be increased to keep brute-force attacks infeasible.
- It automatically embeds a random salt into every hash, so two identical passwords
  produce different hashes — protecting against rainbow-table attacks.
- passlib's CryptContext provides a clean abstraction that makes future algorithm
  upgrades (e.g., migrating to argon2) a one-line configuration change.

Usage example:
--------------
    hashed = hash_password("my_secret")
    is_valid = verify_password("my_secret", hashed)   # True
    is_valid = verify_password("wrong_pass", hashed)  # False
"""

from passlib.context import CryptContext

# -----------------------------------------------------------------------
# CryptContext Configuration
# -----------------------------------------------------------------------
# `schemes`     : Ordered list of algorithms to support. bcrypt is first
#                 (and the only active scheme used for *new* hashes).
# `deprecated`  : "auto" tells passlib to automatically flag older schemes
#                 as deprecated so they can be upgraded on next login.
# -----------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    Hash a plain-text password using bcrypt via passlib.

    What happens internally:
    ------------------------
    1. passlib generates a random 22-character salt.
    2. bcrypt applies its key-expansion cipher using the cost factor (default=12),
       which means 2^12 = 4,096 iterations — slow enough to deter brute force,
       fast enough for real users (< 300 ms on modern hardware).
    3. The resulting hash string encodes: algorithm, cost, salt, and digest
       in a single portable string, e.g.:
           $2b$12$<22-char-salt><31-char-digest>

    Args:
        plain_password (str): The raw password string to be hashed.

    Returns:
        str: A 60-character bcrypt hash string safe to store in the database.
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a stored bcrypt hash.

    What happens internally:
    ------------------------
    passlib extracts the salt and cost factor from the stored hash, re-applies
    bcrypt to the plain-text password with those same parameters, then performs
    a constant-time comparison of the two resulting digests.

    Using constant-time comparison (via `hmac.compare_digest`) is critical: a
    naive `==` comparison could leak timing information, allowing an attacker to
    infer partial hash values character-by-character.

    Args:
        plain_password (str):   The raw password supplied by the user.
        hashed_password (str):  The bcrypt hash retrieved from the database.

    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)
