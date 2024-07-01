from bcrypt import checkpw, gensalt, hashpw


def hash_password(password: str):
    return hashpw(password.encode(), gensalt()).decode()


def check_password(password: str, hashed_password: str):
    return checkpw(password.encode(), hashed_password.encode())
