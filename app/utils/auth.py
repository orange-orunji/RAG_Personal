from jose import jwt
from passlib.context import CryptContext
from datetime import datetime,timedelta

SECRET_ID = "my_secret_key_for_demo" # 加密前缀
ALGORITHM = "HS256" # 加密方式
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24*7 # JWT令牌存在时间
# 生成加密上下文文本对象
pwd_content = CryptContext(schemes=["pbkdf2_sha256"],deprecated="auto")

def generate_hash_password(password : str) -> str:
    """加密明文密码成指定的加密后的密码"""
    return pwd_content.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验密码和目标哈希值是否一样"""
    return pwd_content.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """生成JWT令牌方法"""
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_ID, algorithm=ALGORITHM)


def decode_token(token : str) -> dict:
    """解析JWT令牌方法,拿到令牌中的用户信息"""
    return jwt.decode(token,SECRET_ID,algorithms=[ALGORITHM])