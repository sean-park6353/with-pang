from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # 세션에 사용되는 비밀키를 설정합니다.

CORS(app, supports_credentials=True)

# 데이터베이스 설정
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')

db = SQLAlchemy(app)

# 사용자 모델 정의


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'


# 데이터베이스 초기화 및 테이블 생성
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        return "GET요청"
    return "POST요청"

# 로그인 라우터
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            data = request.get_json()
            id = data.get('id')
            password = data.get('password')
            return f"id는 {id}이며 password는 {password}입니다"
        except Exception as e:
            print(e)

    else:
        return "ㅇㅇㅇ"

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
    app.run(host='0.0.0.0')