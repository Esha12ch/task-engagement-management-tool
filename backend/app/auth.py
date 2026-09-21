from datetime import datetime, timedelta, timezone

from jose import jwt # pyright: ignore[reportMissingModuleSource]
from passlib.context import CryptContext # pyright: ignore[reportMissingImports]


# =========================
# JWT CONFIGURATION
# =========================

SECRET_KEY = "change-this-secret-key-in-production"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


# =========================
# PASSWORD HASHING
# =========================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# =========================
# CREATE JWT TOKEN
# =========================

def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None
) -> str:

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=15
        )

    # Convert datetime to Unix timestamp.
    # This prevents "datetime is not JSON serializable".
    to_encode["exp"] = int(expire.timestamp())

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt