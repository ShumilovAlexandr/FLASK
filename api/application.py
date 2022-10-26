import os

from flask import Flask, request, jsonify
from flask_login import login_required, \
                        LoginManager, logout_user
from flask_jwt_extended import create_access_token
from dotenv import load_dotenv
from psycopg2 import IntegrityError

from database import db_session
from models import User


load_dotenv()

app = Flask(__name__)

login_manager = LoginManager(app)

app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY')
app.config["REFRESH_EXP_LENGTH"] = os.getenv('REFRESH_EXP_LENGTH')
app.config["ACCESS_EXP_LENGTH"] = os.getenv('REFRESH_EXP_LENGTH')
app.config["TOKEN_SECRET_KEY"] = os.getenv('TOKEN_SECRET_KEY')


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


"""Роутер регистрации пользователя"""
@app.route('/signup', methods=["POST"])
def register():
    try:
        email = request.get_json("email", None)
        password = request.get_json("password", None)
        if not email or not password:
            return {"message": "Missing email or password"}
        password_hash = User.set_password(password)
        new_user = User(email=email, password=password_hash)
        db_session.add(new_user)
        db_session.commit()
        return {"username": new_user.username, "email": new_user.email, "password": new_user.password_hash}
    except IntegrityError:
        db_session.rollback()
        return jsonify({"message": "User already exists"}), 400
    except AttributeError:
        return jsonify({"message": "Provide an email and password in JSON format in the request body"}), 400


"""Роутер аутентификации пользователя"""
@app.route('/login', methods=['POST'])
def login():
    email = request.get_json("email", None)
    password = request.get_json("password", None)
    new_user = User.query.filter_by(email=email).first()
    if not email or not new_user.check_password(password):
        return jsonify({"message": "Bad username or password"}), 401
    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token)


"""Роутер отвечающий за выход пользователя"""
@app.route('/logout')
@login_required
def logout():
    logout_user
    return jsonify({"message": "The user logged out"})


#"""Роутер главной страницы, отвечающий за загрузку файла"""
#@app.route('/main')
#@login_required
#def upload_a_file():
#    pass


@login_manager.user_loader
def load_user(user_id):
    return User.get_id(user_id)


if __name__ == "__main":
    app.run()