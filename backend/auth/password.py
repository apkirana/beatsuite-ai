"""
Password hashing.

Passwords are stored as salted PBKDF2-HMAC-SHA256 digests in the format:

    pbkdf2_sha256$<iterations>$<salt_hex>$<derived_key_hex>

Every password gets its own 16-byte random salt, so two users who happen to
choose the same password no longer share a stored value.

Earlier versions of this project stored a bare, unsalted SHA-256 hex digest.
Those are still *verifiable* so existing installations keep working, but they
are treated as compromised: `needs_rehash()` returns True for them and the
login route transparently re-hashes the password on the next successful login.
Unsalted SHA-256 is unsuitable for passwords — it is fast enough to brute-force
at billions of guesses per second and falls to precomputed rainbow tables.
"""

import hashlib
import hmac
import os
import secrets
import string

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 600_000          # OWASP guidance for PBKDF2-HMAC-SHA256
SALT_BYTES = 16


def hash_password(password: str, *, iterations: int = ITERATIONS) -> str:
    """Hash a password with a fresh random salt."""
    if not password:
        raise ValueError("Password must not be empty")

    salt = os.urandom(SALT_BYTES)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"{ALGORITHM}${iterations}${salt.hex()}${derived.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """
    Check a password against a stored hash, in constant time.

    Accepts both the current salted format and the legacy unsalted SHA-256
    digest, so an existing users.json keeps working across the upgrade.
    """
    if not password or not stored:
        return False

    if stored.startswith(f"{ALGORITHM}$"):
        try:
            _, iterations, salt_hex, expected_hex = stored.split("$", 3)
            derived = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations)
            )
        except (ValueError, TypeError):
            return False
        return hmac.compare_digest(derived.hex(), expected_hex)

    # Legacy: bare unsalted SHA-256 hex digest.
    legacy = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(legacy, stored)


def needs_rehash(stored: str) -> bool:
    """True if a stored hash uses a legacy or weaker-than-current scheme."""
    if not stored or not stored.startswith(f"{ALGORITHM}$"):
        return True
    try:
        iterations = int(stored.split("$", 2)[1])
    except (ValueError, IndexError):
        return True
    return iterations < ITERATIONS


def generate_password(length: int = 20) -> str:
    """Generate a random password for seeding accounts."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*-_"
    return "".join(secrets.choice(alphabet) for _ in range(length))
