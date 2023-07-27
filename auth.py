import jwt
from datetime import datetime, timedelta
from flask import current_app

def generate_jwt(user_id, email):
    access_token_payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=1),  # JWT 만료 시간 설정 (예: 1시간)
    }
    refresh_token_payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(hours=10),  # JWT 만료 시간 설정 (예: 1시간)
    }
    # JWT를 생성하고 반환합니다.
    access_token = jwt.encode(access_token_payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    refresh_token = jwt.encode(refresh_token_payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return access_token, refresh_token

def verify_jwt(jwt_token):
    try:
        # JWT를 검증하고 payload를 디코딩합니다.
        payload = jwt.decode(jwt_token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        # JWT의 유효 기간이 만료되었을 경우 처리할 내용을 여기에 추가합니다.
        return None
    except jwt.InvalidTokenError:
        # 유효하지 않은 JWT인 경우 처리할 내용을 여기에 추가합니다.
        return None