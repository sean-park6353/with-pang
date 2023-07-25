import jwt
from datetime import datetime, timedelta
from flask import current_app

def generate_jwt(user_id):
    # JWT payload에 담을 정보를 설정합니다.
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=1),  # JWT 만료 시간 설정 (예: 1시간)
    }

    # JWT를 생성하고 반환합니다.
    jwt_token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return jwt_token

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