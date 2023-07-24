from flask import Flask, request, redirect, url_for, session, jsonify, make_response
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, User
import os
import ssl

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
    
    
@app.before_request
def before_request():
    if request.endpoint not in ['main', 'signin', 'signup', 'dashboard', 'logout']:
        return redirect(url_for('main'))

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        return "main에 대한 GET요청"
    return "main에 대한 POST요청"

@app.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    login_id = data.get('signinId')
    password = data.get('signinPw')
    user = User.query.filter_by(login_id=login_id, password=password).first()
    if user:
        session["user_id"] = user.id
        response = {"result": "성공", "code": "S001"}
        return make_response(jsonify(response), 200)
    
    response = {"result": "아이디와 패스워드를 확인해주세요", "code": "E001"}
    return make_response(jsonify(response), 400)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    login_id = data.get('signupId')
    password = data.get('signupPw')

    # 이미 존재하는 사용자인지 확인
    user = User.query.filter_by(login_id=login_id).first()
    if user:
        response = {"result": "이미 가입된 회원입니다", "code": "E001"}
        return make_response(jsonify(response), 400)

    # 새로운 사용자 추가
    new_user = User(login_id=login_id, password=password)
    db.session.add(new_user)
    db.session.commit()

    response = {"result": "성공", "code": "S001"}
    return make_response(jsonify(response), 200)


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
    app.run(host='0.0.0.0', port=443, ssl_context=('cert.pem', 'key.pem'))