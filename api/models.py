from flask_login import UserMixin
from flask_jwt_extended import create_access_token
from werkzeug.security import (generate_password_hash, 
                               check_password_hash)

from . import db as db 
from . import app as app


class User(db.Model, UserMixin):
    """Модель пользователя."""
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text(), nullable=False)

    def __repr__(self):
        return self.username

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)
    
    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_token(self):
        token = create_access_token(identity=self.email)
        return token

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def get_id(self):
        return self.id


with app.app_context():
    db.create_all()
