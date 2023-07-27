from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from datetime import datetime

db = SQLAlchemy()
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login_id = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Add the created_at column with a default value
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 
    is_active = db.Column(db.Boolean, default=True)
    
    # Board와의 관계 설정
    boards = relationship('Board', back_populates='author')
    
    def __repr__(self):
        return f'<User {self.login_id}>'

class Board(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    content = db.Column(db.String(200), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Add the created_at column with a default value
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 

    # User와의 관계 설정
    author = relationship('User', back_populates='boards')
    
    def __repr__(self):
        return f'<Board {self.title}>'
    
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'author_id': self.author.login_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'views': self.views
        }

        
class UserAuth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Add the created_at column with a default value
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 
    is_valid = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<user_auth {self.id}>'
    
class LikeBoard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'), nullable=False)
    is_like = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 
    
    def __repr__(self):
        return f'<LikeBoard user_id:{self.user_id} board_id:{self.board_id} is_like:{self.is_like}>'



