from flask import Flask, request, session, jsonify, make_response, g
from sqlalchemy import desc, func
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, User, UserAuth, Board, LikeBoard
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
        token = request.headers.get('Authorization')

        if not token:
            response = {"result": "로그인이 필요합니다", "code": "E002"}
            return make_response(jsonify(response), 401)

        auth = session.query(UserAuth).order_by(desc(UserAuth.created_at)).first()
        payload = verify_jwt(token)
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
        response = {
            "result": "성공", 
            "code": "S001", 
            "token": token
        }
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
@app.route('/board')
@required_login
def dashboard():
    app.logger.info(f'Welcome, {g.current_user_id}! This is your dashboard. ')
    like_count_subquery = db.session.query(
        func.count(LikeBoard.id)
    ).filter(
        LikeBoard.is_like == True,
        LikeBoard.board_id == Board.id
    ).label('likes')
    boards_with_likes = db.session.query(Board, like_count_subquery).order_by(Board.created_at.desc()).all()
    data_list = []
    for board, like_count in boards_with_likes:
        serialized_board = board.serialize()
        serialized_board['likes'] = like_count
        data_list.append(serialized_board)
    return make_response(jsonify({"result": "성공", "code": "S001", "data_list": data_list}), 200)
    
# 로그아웃 라우터
@app.route('/signout', methods=["POST"])
def logout():
    data = request.get_json()
    user_id = data.get("userId")
    auth = session.query(UserAuth).join(User, UserAuth.user_id == User.id).order_by(UserAuth.created_at.desc()).filter(User.login_id==user_id).all()[0]
    auth.is_valid = False
    session.commit()
    app.logger.info(f"사용자 로그아웃 login_id: {request.headers}, request_data={data}")  # 로그 추가
    return make_response(jsonify({"result": "성공", "code": "S001"}), 200)

# 글쓰기(Create) API
@app.route('/board', methods=['POST'])
def create_board():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    author = data.get('author')
    user = session.query(User).filter(User.login_id == author).first()
    if not title or not content:
        response = {"result": "제목과 내용을 모두 입력해주세요.", "code": "E001"}
        return jsonify(response), 400

    new_board = Board(title=title, content=content, author_id=user.id)
    try:
        # 데이터베이스에 새로운 Board 저장
        db.session.add(new_board)
        db.session.commit()
        response = {"result": "글쓰기가 성공적으로 완료되었습니다.", "code": "S001"}
        return jsonify(response), 200  # Created
    except Exception as e:
        db.session.rollback()
        app.logger.info(e)
        response = {"result": "글쓰기에 실패했습니다. 다시 시도해주세요.", "code": "E002"}
        return jsonify(response), 500

# 글 삭제(Delete) API
@app.route('/board', methods=['DELETE'])
def delete_board():
    data = request.get_json()
    board_id = data.get("boardId")
    try:
        session.query(Board).filter(Board.id==board_id).delete()
        db.session.commit()
        response = {"result": "글 삭제가 성공적으로 완료되었습니다.", "code": "S002"}
        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        app.logger.info(e)
        response = {"result": "글 삭제에 실패했습니다. 다시 시도해주세요.", "code": "E004"}
        return jsonify(response), 500


# 글 수정(Update) API
@app.route('/board', methods=['PUT'])
def update_board():
    data = request.get_json()
    board_id = data.get("boardId")
    new_content = data.get("content")

    try:
        # 해당 board_id에 해당하는 글이 존재하는지 확인
        board = session.query(Board).filter(Board.id == board_id).first()

        if not board:
            response = {"result": "해당하는 글이 존재하지 않습니다.", "code": "E005"}
            return jsonify(response), 404

        # 글의 내용(content)을 업데이트하고 DB에 반영
        board.content = new_content
        db.session.commit()

        response = {"result": "글 수정이 성공적으로 완료되었습니다.", "code": "S003"}
        return jsonify(response), 200

    except Exception as e:
        db.session.rollback()
        app.logger.info(e)
        response = {"result": "글 수정에 실패했습니다. 다시 시도해주세요.", "code": "E006"}
        return jsonify(response), 500


# 좋아요 기능 및 좋아요 취소 기능 토글 엔드포인트
@app.route('/board/likes', methods=['POST'])
def toggle_like():
    data = request.get_json()
    user_id = data.get('userId')
    board_id = data.get('boardId')
    user = session.query(User).filter(User.login_id==user_id).first()
    
    # LikeBoard 객체를 가져오기
    like_board = db.session.query(LikeBoard).filter_by(user_id=user.id, board_id=board_id).first()

    if like_board and like_board.is_like:
        like_board.is_like = False
        session.commit()
        response = {'result': like_board.is_like, "code": "S001"}
        
    elif not like_board:
        new_like = LikeBoard(user_id=user.id, board_id=board_id, is_like=True)
        db.session.add(new_like)
        db.session.commit()
        response = {'result': new_like.is_like, "code": "S001"}

    else:
        like_board.is_like = True
        db.session.commit()
        response = {'result': like_board.is_like, "code": "S001"}
        
    return jsonify(response)



if __name__ == '__main__':
    app.run( host='0.0.0.0', port=5000)