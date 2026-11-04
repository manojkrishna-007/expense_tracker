from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

# Password hashing setup using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Secret key for signing session cookies
SECRET_KEY = "super-secret-money-manager-key-change-in-production"
serializer = URLSafeTimedSerializer(SECRET_KEY)

def hash_password(password: str) -> str:
    # Truncate to 72 bytes to prevent any bcrypt input limits
    encoded_pwd = password.encode('utf-8')[:72]
    return pwd_context.hash(encoded_pwd.decode('utf-8', errors='ignore'))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    encoded_pwd = plain_password.encode('utf-8')[:72]
    return pwd_context.verify(encoded_pwd.decode('utf-8', errors='ignore'), hashed_password)

def create_session_token(user_id: int) -> str:
    return serializer.dumps({"user_id": user_id})

def verify_session_token(token: str, max_age: int = 86400) -> int | None:
    """Verifies cookie token. Max age defaults to 24 hours (86400 seconds)."""
    try:
        data = serializer.loads(token, max_age=max_age)
        return data.get("user_id")
    except (BadSignature, SignatureExpired):
        return None