from django.http import JsonResponse
from .utils import verify_jwt


class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.headers.get("Authorization")  # Tokenni header'dan olish
        if token:
            token = token.replace("Bearer ", "")  # "Bearer " ni olib tashlash
            payload = verify_jwt(token)
            if payload:
                request.user_id = payload[
                    "user_id"
                ]  # Foydalanuvchi ID sini so'rovlarga qo'shish
            else:
                return JsonResponse({"error": "Invalid token or expired"}, status=401)
        return self.get_response(request)
