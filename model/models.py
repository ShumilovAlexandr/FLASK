
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, \
                              check_password_hash

from . import db, app


class User(db.Model, UserMixin):
    """Модель пользователя."""
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text(15), nullable=False)

    def __repr__(self):
        return self.username

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def set_password(self, password):
        """Функция перевода исходного пароля в хэш-значение."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Функция сравнения хэша пароля из базы со значением введенным пользователем."""
        return check_password_hash(self.password_hash, password)

