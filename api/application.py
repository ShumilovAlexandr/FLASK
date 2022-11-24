import psycopg2

from flask import request, jsonify
from flask_jwt_extended import JWTManager
from psycopg2 import IntegrityError
from model.models import User, db, app


jwt = JWTManager(app)

connection = psycopg2.connect(dbname="flaskapp", user="postgres", password="postgres",
                              host="localhost")


@app.route('/signup', methods=["POST"])
def register():
    """
    Функция регистрации пользователя.
    
    В случае успешной регистрации пользователя, возвращается токен.
    """
    try:
        params = request.json
        new_user = User(**params)
        db.session.add(new_user)
        db.session.commit()
        access_token = new_user.get_token()
        return {"access_token": access_token}
    except TypeError:
        db.session.rollback()


#@app.route('/login', methods=["POST"])
#def login():
#    """Функция логина пользователя."""
#    email = request.get_json("email", None)
#    password = request.get_json("password", None)
#    if not email or not password:
#        return jsonify({"message": "Bad username or password"}), 400
#    new_user = User.query.filter(email == email).first()                    #TODO не работает мать его растак
#    if not new_user:
#        return jsonify({"message": "User not found"}), 404
#    login_user(new_user)
#    access_token = create_access_token(identity={"email": email})
#    return jsonify({"access_token": access_token}), 200


#"""Роутер отвечающий за выход пользователя"""
#@app.route('/logout')                              ## TODO доделать
#@login_required                                    
#def logout():
#    logout_user
#    return jsonify({"message": "The user logged out"})
#
#


@app.route('/users', methods=["GET"])
def get_users():
    """
    Функция для возврата всех пользователей из базы данных.
    
    В ТЗ не было задачи сделать такую функцию, но решил ее организовать
    для проверки общего количества записей в БД о пользователях.
    """
    try:
        cursor = connection.cursor()
        cursor.execute('SELECT users.id, users.email, users.username FROM users')
        row = cursor.fetchall()
        return jsonify(row)
    except Exception as e:
        return e


@app.route('/users/<int:id>/', methods=["GET", "DELETE"])
def get_or_delete_single_user(id):
    """
    Функция для возврата или удаления коткретного пользователя из базы данных.
    
    В ТЗ не было задачи сделать такую функцию, но решил ее организовать
    для того чтобы можно было подчистить БД от лишних пользователей,
    которых насоздавал во время тестирования приложения.
    """
    if request.method == "GET":
        try:
            cursor = connection.cursor()
            cursor.execute('SELECT users.id, users.email, users.username FROM users WHERE id = {}'.format(id))
            row = cursor.fetchone()
            return jsonify(row)
        except Exception as e:
            return e
    else:
        try:
            if request.method == "DELETE":
                cursor = connection.cursor()
                cursor.execute('DELETE FROM users WHERE id = {}'.format(id))
                connection.commit()
                row = cursor.rowcount
                return jsonify(f"Общее количество удаленных записей - {row}", "Запись под номером {} успешно удалена".format(id))
        except Exception as e:
            return e


##"""Роутер главной страницы, отвечающий за загрузку файла"""
##@app.route('/main')
##@login_required
##def upload_a_file():
##    ...



if __name__ == "__main":
    app.run(host='127.0.0.1', port='5000')