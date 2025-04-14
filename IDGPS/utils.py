import jwt
from datetime import datetime, timedelta
from django.conf import settings

# Maxfiy kalitni settings.py faylida saqlang
SECRET_KEY = settings.SECRET_KEY


# JWT yaratish
def create_jwt(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=1),  # Tokenning amal qilish muddati
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


# JWT tekshirish
def verify_jwt(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token muddati o'tgan
    except jwt.InvalidTokenError:
        return None  # Noto'g'ri token
