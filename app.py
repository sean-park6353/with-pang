from flask import Flask, request, session, jsonify, make_response, g
from sqlalchemy import desc
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, User, UserAuth
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from functools import wraps
from auth import generate_jwt, verify_jwt
import os
import logging
# Session 객체 생성
session = db.session

# 로그 설정
log_formatter = logging.Formatter('[%(asctime)s %(levelname)s] %(name)s - %(message)s')
file_handler = logging.FileHandler('logs/app.log')
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.DEBUG)

load_dotenv()
app = Flask(__name__)
app.secret_key = 'your-secret-key'  # 세션에 사용되는 비밀키를 설정합니다.
app.config['JWT_SECRET_KEY'] = 'your-jwt-secret-key'  # JWT에 사용되는 비밀키를 설정합니다.
app.config['JWT_EXPIRATION_DELTA'] = timedelta(hours=1)  # JWT의 만료 시간을 설정합니다.

CORS(app, supports_credentials=True)

def required_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        jwt_token = request.headers.get('Authorization')

        if not jwt_token:
            response = {"result": "로그인이 필요합니다", "code": "E002"}
            return make_response(jsonify(response), 401)

        # JWT 검증을 수행합니다.
        payload = verify_jwt(jwt_token)
        auth = session.query(UserAuth).filter(UserAuth.token==jwt_token).first()
        if not payload or not auth.is_valid:
            response = {"result": "유효하지 않은 토큰입니다", "code": "E002"}
            return make_response(jsonify(response), 401)

        g.current_user_id = payload["user_id"]

        return f(*args, **kwargs)
    return decorated_function

# 데이터베이스 설정
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
db.init_app(app)
migrate = Migrate(app, db)

# 데이터베이스 초기화 및 테이블 생성
with app.app_context():
    db.create_all()

# 로그 설정 추가
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.DEBUG)

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        return "main에 대한 GET요청"
    return "main에 대한 POST요청"

@app.route('/signin', methods=['POST'])
def signin():
    app.logger.info("signin 요청")
    data = request.get_json()
    login_id = data.get('signinId')
    password = data.get('signinPw')
    user = session.query(User).filter(User.login_id==login_id).first()

    if user and check_password_hash(user.password, password):
        app.logger.info(f"signin 성공: {login_id}, request_data={data}")
        token = generate_jwt(user.id)
        new_auth = UserAuth(user_id=user.id, token=token, is_valid=True)
        session.add(new_auth)
        session.commit()
        response = {"result": "성공", "code": "S001", "token": token}
        return make_response(jsonify(response), 200)
    
    app.logger.warning("signin 실패: 아이디와 패스워드를 확인해주세요")
    response = {"result": "아이디와 패스워드를 확인해주세요", "code": "E001"}
    return make_response(jsonify(response), 400)

@app.route('/signup', methods=['POST'])
def signup():
    app.logger.info("signup 요청")
    data = request.get_json()
    login_id = data.get('signupId')
    password = data.get('signupPw')

    # 이미 존재하는 사용자인지 확인
    user = session.query(User).filter(User.login_id==login_id).first()
    if user:
        app.logger.warning(f"signup 실패: 이미 가입된 회원입니다. user_id: {user.id}, request_data={data}")
        response = {"result": "이미 가입된 회원입니다", "code": "E001"}
        return make_response(jsonify(response), 400)

    hashed_password = generate_password_hash(password)
    new_user = User(login_id=login_id, password=hashed_password, created_at=datetime.utcnow())
    db.session.add(new_user)
    db.session.commit()
    app.logger.info(f"signup 성공. login_id: {login_id}, request_data={data}") 
    response = {"result": "성공", "code": "S001"}
    return make_response(jsonify(response), 200)


# 대시보드 라우터
@app.route('/dashboard')
@required_login
def dashboard():
    user_id = g.current_user_id
    user = session.query(User).filter(User.id==user_id).first()
    app.logger.info(f'Welcome, {user.login_id}! This is your dashboard. ')
    data_list = [
        {
            "board_id": 1,
            "title": "게시판 제목",
            "content": "여기에는 컨텐츠내용이 들어가요~~"
        },
        {
            "board_id": 2,
            "title": "게시판 제목2222",
            "content": "여기에는 컨텐츠내용이 들어가요~~222222222"
        }
    ]
    return make_response(jsonify({"result": "성공", "code": "S001", "data_list": data_list}), 200)
    
# 로그아웃 라우터
@app.route('/signout', methods=["POST"])
def logout():
    data = request.get_json()
    user_id = data.get("userId")
    if user_id:
        auth = session.query(UserAuth, User).join(UserAuth.user_id == User.id).filter(User.login_id==user_id).order_by(desc(UserAuth.created_at)).first()
        auth.is_valid = False
        session.commit()
        app.logger.info(f"사용자 로그아웃 login_id: {request.headers}, request_data={data}")  # 로그 추가
        return make_response(jsonify({"result": "성공", "code": "S001"}), 200)


if __name__ == '__main__':
    app.run( host='0.0.0.0', port=5000)