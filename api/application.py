import psycopg2

from flask import request, jsonify, redirect, url_for
from flask_jwt_extended import JWTManager
from flask_login import login_user, \
                        logout_user, \
                        login_required, \
                        current_user


from model.models import User, db, app, login_manager


login_manager.login_view = 'login'

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


@app.route('/login', methods=["POST"])
def login():
    """Функция логина пользователя."""
    if current_user.is_authenticated:                           #TODO ошибка вот здесь, в is_authenticated. Нет такого метода 
        return redirect(url_for('upload_a_file'))
    if request.method == 'POST':
        params = request.json
        user = User(**params)
        if user.check_password(user.password):
            login_user(user)
    return redirect('upload_a_file')


#@app.route('/logout')                              ## TODO это во вторую
#@login_required                                    
#def logout():
#"""Функция отвечающая за выход пользователя"""
#    logout_user()
#    return redirect('Пользователь вышел из приложения', \
#                     url_for('login'))


@app.route('/users', methods=["GET"])
def get_users():
    """
    Функция для возврата всех пользователей из базы данных.
    
    В ТЗ не было задачи сделать такую функцию, но решил ее организовать
    для проверки общего количества записей в БД о пользователях.
    """
    try:
        cursor = connection.cursor()
        cursor.execute('SELECT users.id, users.username, users.email, users.password FROM users')
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


"""Роутер главной страницы, отвечающий за загрузку файла"""
@app.route('/process')
@login_required
def upload_a_file():              # TODO как только будет работать эта функция, проект готов. Нужно, чтобы файл загружался, обрабатывался, и выгружался результат
    return                        # Точнее, еще настоить GraphQL



if __name__ == "__main":
    app.run(host='127.0.0.1', port='5000')