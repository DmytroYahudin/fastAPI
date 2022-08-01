from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def password_hash(password: str):
    return pwd_context.hash(password)


def verify(palin_password, hashed_password):
    return pwd_context.verify(palin_password, hashed_password)
