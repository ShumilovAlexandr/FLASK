from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
#from datetime import timedelta


from application import db_session


class User(db_session.Model, UserMixin):
    """Модель пользователя."""
    __tablename__ = 'users'
    id = db_session.Column(db_session.Integer(), primary_key=True)
    username = db_session.Column(db_session.String(80), unique=True, nullable=False)
    email = db_session.Column(db_session.String(120), unique=True, nullable=False)
    password = db_session.Column(db_session.Text(15), nullable=False)

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

##    def get_token(self, expire_time=24):
##        expire_delta = timedelta(expire_time)
##        token = create_access_token(
##            identity=self.id,
##            expires_delta=expire_delta
##        )
##        return token