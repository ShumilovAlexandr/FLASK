from flask import request, jsonify
from flask_login import LoginManager, login_user
from flask_jwt_extended import JWTManager, create_access_token
from psycopg2 import IntegrityError

from model.models import User, db, app

#app.config["REFRESH_EXP_LENGTH"] = os.getenv('REFRESH_EXP_LENGTH')
#app.config["ACCESS_EXP_LENGTH"] = os.getenv('REFRESH_EXP_LENGTH')
#app.config["TOKEN_SECRET_KEY"] = os.getenv('TOKEN_SECRET_KEY')

login_manager = LoginManager(app)

jwt = JWTManager(app)

#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#
#engine = create_engine(os.getenv('SQLALCHEMY_DATABASE_URL'))
#session = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))


#@app.teardown_appcontext
#def shutdown_session(exception=None):
#    session.remove()
#
#
"""Роутер регистрации пользователя"""
@app.route('/signup', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        try:
            params = request.json
            new_user = User(**params)
            db.session.add(new_user)
            db.session.commit()
            return ({"id": new_user.id, 
                     "username": new_user.username, 
                     "email": new_user.email, 
                     "password": new_user.password_hash})
        except IntegrityError:
            db.session.rollback()
            return jsonify({"message": "User already exists"}), 400
        except AttributeError:
            return jsonify({"message": "Provide an email and password in JSON format in the request body"}), 400


"""Роутер аутентификации пользователя"""
@app.route('/login', methods=['POST'])
def login():
    email = request.get_json("email", None)
    password = request.get_json("password", None)
    new_user = db.session.query(User).filter(User.email == email).first()
    if not email or not new_user.check_password(password):
        return jsonify({"message": "Bad username or password"}), 401
    login_user(new_user)
    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token)


#"""Роутер отвечающий за выход пользователя"""
#@app.route('/logout')
#@login_required
#def logout():
#    logout_user
#    return jsonify({"message": "The user logged out"})
#
#
##"""Роутер для проверки пользователей в базе данных"""
##@app.route('/users', methods=['GET', "DELETE"])
##def check_users():
##    ...
#
##"""Роутер главной страницы, отвечающий за загрузку файла"""
##@app.route('/main')
##@login_required
##def upload_a_file():
##    pass
#
#
@login_manager.user_loader
def load_user(user_id):
    return User.get_id(user_id)


if __name__ == "__main":
    app.run(host='127.0.0.1', port='5000')