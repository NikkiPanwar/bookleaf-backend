import hmac
import hashlib
import json
import base64
import time
from datetime import datetime, timedelta
from typing import Optional, Any, Dict
from app.core.config import settings

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt (or sha256 salt fallback)."""
    try:
        import bcrypt
        pwd_bytes = password.encode("utf-8")[:72]
        return bcrypt.hashpw(pwd_bytes, bcrypt.gensalt()).decode("utf-8")
    except Exception:
        salt = settings.SECRET_KEY[:16]
        return hashlib.sha256((salt + password).encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    try:
        import bcrypt
        if hashed_password.startswith(("$2a$", "$2b$", "$2y$")):
            pwd_bytes = plain_password.encode("utf-8")[:72]
            return bcrypt.checkpw(pwd_bytes, hashed_password.encode("utf-8"))
    except Exception:
        pass

    salt = settings.SECRET_KEY[:16]
    expected = hashlib.sha256((salt + plain_password).encode()).hexdigest()
    return hmac.compare_digest(expected, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": int(expire.timestamp())})

    try:
        import jwt
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    except ImportError:
        # Standard lightweight JWT implementation
        header = {"alg": "HS256", "typ": "JWT"}
        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
        payload_b64 = base64.urlsafe_b64encode(json.dumps(to_encode).encode()).decode().rstrip("=")
        signing_input = f"{header_b64}.{payload_b64}".encode()
        signature = hmac.new(settings.SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
        sig_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")
        return f"{header_b64}.{payload_b64}.{sig_b64}"

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate JWT access token."""
    try:
        import jwt
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except ImportError:
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None
            header_b64, payload_b64, sig_b64 = parts
            signing_input = f"{header_b64}.{payload_b64}".encode()
            expected_sig = hmac.new(settings.SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
            # Add padding
            rem = len(sig_b64) % 4
            if rem > 0:
                sig_b64 += "=" * (4 - rem)
            provided_sig = base64.urlsafe_b64decode(sig_b64)
            if not hmac.compare_digest(expected_sig, provided_sig):
                return None
            rem_p = len(payload_b64) % 4
            if rem_p > 0:
                payload_b64 += "=" * (4 - rem_p)
            payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode())
            if "exp" in payload and payload["exp"] < time.time():
                return None
            return payload
        except Exception:
            return None
