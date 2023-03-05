import psycopg2
import aiofiles
import os

from flask import (request, 
                   jsonify)
from werkzeug.utils import secure_filename
from flask_login import (login_user, 
                         logout_user,
                         login_required,
                         LoginManager)
from flask_jwt_extended import JWTManager
from flask_graphql import GraphQLView

from . import db as db 
from . import app as app
from .models import User
from .schema import schem 


jwt = JWTManager(app)

login_manager = LoginManager(app)

connection = psycopg2.connect(dbname="flaskapp", user="postgres",
                              password="postgres",
                              host="localhost")
cursor = connection.cursor()


@login_manager.user_loader
def load_user(id):
    return User.query.get(str(id))


app.config['UPLOAD_FOLDER'] == \
        os.getenv('UPLOAD_FOLDER')

ALLOWED_EXTENSIONS = {'txt'}


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
async def login():
    """Функция логина пользователя."""
    params = request.json
    user = User(**params)
    check_user = User.query.filter_by(username=user.username,
                                      email=user.email).first()
    login_user(check_user)
    return jsonify({'Сообщение': 'Пользователь {} '
                                 'успешно авторизован.'.format(user.username)})


@app.route('/logout', methods=["POST"])
@login_required                        
def logout():
    """Функция отвечающая за выход пользователя."""
    logout_user()
    return jsonify({"Результат": "200",
                    "Cообщение": "Выход пользователя выполнен"})


@app.route('/users', methods=["GET"])
def get_users():
    """
    Функция для возврата всех пользователей из базы данных.
    
    В ТЗ не было задачи сделать такую функцию, но решил ее организовать
    для проверки общего количества записей в БД о пользователях.
    """
    try:
        cursor.execute('SELECT users.id, users.username, '
                       'users.email, users.password FROM users')
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
            cursor.execute('SELECT users.id, users.email, '
                           'users.username FROM users '
                           'WHERE id = {}'.format(id))
            row = cursor.fetchone()
            return jsonify(row)
        except Exception as e:
            return e
    else:
        try:
            if request.method == "DELETE":
                cursor.execute('DELETE FROM users WHERE id = {}'.format(id))
                connection.commit()
                row = cursor.rowcount
                return jsonify(
                    {"Количество": f"Общее количество "
                                   f"удаленных записей - {row}",
                     "Сообщение": "Запись под номером {} успешно "
                                  "удалена".format(id)})
        except Exception as e:
            return e


async def process_the_file(filename):
    """Роутер, отвечающий за Обработку файла."""
    async with aiofiles.open(app.config['UPLOAD_FOLDER'] + filename,
                             mode='r') as file:
        contents = await file.read()
        count = len(contents)
        line_count = 0
        file_name = os.path.basename(app.config['UPLOAD_FOLDER'] + filename)
        size_file = os.stat(app.config['UPLOAD_FOLDER'] + filename).st_size
        for _ in contents:
            if _ == '\n':
                line_count += 1
        return jsonify({"Название загружаемого файла": f"{file_name}",
                        "Размер загружаемого файла в байтах": f"{size_file}",
                        "Общее количество символов в "
                        "загружаемом файле": f"{count}",
                        "Количество строк в загружаемом "
                        "файле": f"{line_count}"})


async def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/process', methods=["POST", "GET"])
@login_required
async def upload_file():
    """Главный роутер, отвечающий за загрузку файла."""
    if request.method == "POST":
        if 'file' not in request.files:
            return jsonify('Файл с данным именем не найден')
        file = request.files['file']
        if file.filename == '':
            return jsonify('Выберете существующий файл')
        if file and await allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        data = await process_the_file(filename)
        return jsonify({"Данные": data.json,
                        "Сообщение": 'Файл успешно загружен на сервер'})

def graphql():
    view_func = GraphQLView.as_view(
        'graphql',
        schema=schem,
        graphiql=True
        )
    return view_func

app.add_url_rule(
    '/graphql',
    view_func=graphql()
)



if __name__ == "__main":
    app.run(host='127.0.0.1', port='5000')
