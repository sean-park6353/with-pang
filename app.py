from flask import Flask, request, redirect, url_for, session, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
import os
from models import db, User

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # 세션에 사용되는 비밀키를 설정합니다.

CORS(app, supports_credentials=True)

# 데이터베이스 설정
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
db.init_app(app)
migrate = Migrate(app, db)

# 데이터베이스 초기화 및 테이블 생성
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        return "GET요청"
    return "POST요청"

# 로그인 라우터
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    login_id = data.get('loginId')
    password = data.get('loginPw')
    user = User.query.filter_by(login_id=login_id, password=password).first()
    if user:
        session["user_id"] = user.id
        return jsonify(message='성공', status=200)
    return jsonify(message='아이디와 패스워드를 확인해주세요', status=400)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    login_id = data.get('signupId')
    password = data.get('signupPw')

    # 이미 존재하는 사용자인지 확인
    user = User.query.filter_by(login_id=login_id).first()
    if user:
        return jsonify(message='이미 존재하는 사용자입니다.', status=400)

    # 새로운 사용자 추가
    new_user = User(login_id=login_id, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(message='회원가입 성공!', status=200)


# 대시보드 라우터
@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if user_id:
        return f'Welcome, {session["username"]}! This is your dashboard.'
    else:
        return redirect(url_for('login'))
    
# 로그아웃 라우터


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)