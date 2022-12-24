import os
import hashlib
import datetime
import copy
import pymysql
from flask import *
from flask_login import *
import api

app = Flask(__name__)
app.secret_key = os.urandom(16).hex()

# setup logging
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_view = 'login'
login_manager.login_message = 'Please Login'

salt = "VIESHOW"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = pymysql.connect(
            host = 'localhost', 
            port = 3306, 
            user = 'jeffrey', 
            passwd = '', 
            db = 'VIESHOW'
        )
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(user_id):
    password = api.get_member_password(user_id, db = get_db())
    if password is None:
        return
    user = User()
    user.id = user_id
    return user

@login_manager.request_loader
def request_loader(request):
    user_id = request.form.get('ID')
    password = api.get_member_password(user_id, db = get_db())
    if not password:
        return
    user = User()
    user.id = user_id
    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user_password = request.form.get('password')
    user_password += salt
    user_password = hashlib.sha256(user_password.encode()).hexdigest()
    if user_password == password[0]:
        user.is_authenticated = True
    return user

@app.route('/')
def index():
    # to be done: dependent drop down
    return render_template('index.html')

@app.route('/theater')
def theater():
    theaters = list(api.get_all_studios(db = get_db()))
    theaters_pair = []
    for i in range(len(theaters) // 2):
        theaters_pair.append([theaters[i * 2], theaters[i * 2 + 1]])
    if len(theaters) & 1:
        theaters_pair.append([theaters[-1], None])
    return render_template('theater.html', theaters=theaters_pair)

@app.route('/cineplex')
def cineplex():
    name = request.args.get('name')
    info = api.get_studio_info(name, db = get_db())
    sessions_info = api.get_sessions(studio_name = name, db = get_db())
    dates = sorted(list(set(sessions_info['movie_date'])), key = lambda x: datetime.datetime.strptime(x[0], '%Y/%m/%d'))
    movie_list = list(set(sessions_info['movie_info']))
    versions = list(set(sessions_info['movie_version']))
    version_dict = {version: copy.deepcopy([]) for version in versions}
    movie_dict = {movie: copy.deepcopy(version_dict) for movie in movie_list}
    dates_dict = {date: copy.deepcopy(movie_dict) for date in dates}
    for i in range(len(sessions_info['movie_cinema'])):
        dates_dict[sessions_info['movie_date'][i]][sessions_info['movie_info'][i]][sessions_info['movie_version'][i]].append(sessions_info['movie_time'][i])
        dates_dict[sessions_info['movie_date'][i]][sessions_info['movie_info'][i]][sessions_info['movie_version'][i]].sort(key = lambda x: datetime.datetime.strptime(x[0], '%H:%M'))
    return render_template('cineplex.html', info = info, sessions = dates_dict, dates = dates, movies = movie_list, versions = versions)

@app.route('/movies')
def movies():
    movies = list(api.get_all_movies(db = get_db()))
    movies_pair = []
    for i in range(len(movies) // 2):
        movies_pair.append([movies[i * 2], movies[i * 2 + 1]])
    if len(movies) & 1:
        movies_pair.append([movies[-1], None])
    return render_template('movies.html', movies=movies_pair)

@app.route('/movieintro')
def movieintro():
    name = request.args.get('name')
    info = api.get_movie_info(name, db = get_db())
    sessions_info = api.get_sessions(movie_title = name, db = get_db())
    cinemas = list(set(sessions_info['movie_cinema']))
    dates = sorted(list(set(sessions_info['movie_date'])), key = lambda x: datetime.datetime.strptime(x[0], '%Y/%m/%d'))
    versions = list(set(sessions_info['movie_version']))
    version_dict = {version: copy.deepcopy([]) for version in versions}
    movie_dict = {date: copy.deepcopy(version_dict) for date in dates}
    cinema_dict = {cinema: copy.deepcopy(movie_dict) for cinema in cinemas}
    for i in range(len(sessions_info['movie_cinema'])):
        cinema_dict[sessions_info['movie_cinema'][i]][sessions_info['movie_date'][i]][sessions_info['movie_version'][i]].append(sessions_info['movie_time'][i])
        cinema_dict[sessions_info['movie_cinema'][i]][sessions_info['movie_date'][i]][sessions_info['movie_version'][i]].sort(key = lambda x: datetime.datetime.strptime(x[0], '%H:%M'))
    return render_template('movieintro.html', info = info, sessions = cinema_dict, cinemas = cinemas, dates = dates, versions = versions)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template("login.html", next = request.args.get("next"))
    user_id = request.form['account']
    user_password = request.form['password']
    user_password += salt
    user_password = hashlib.sha256(user_password.encode()).hexdigest()
    db = get_db()
    cur = db.cursor()
    cur.execute(
        'SELECT validated FROM members WHERE account = %s', (user_id, )
    )
    validated = cur.fetchone()[0]
    print(validated, "\n\n\n\n\n\n")
    if validated == False:
        errorMsg='<span style="color:#35858B"></span><i class="fa fa-exclamation-triangle" aria-hidden="true"></i>此帳號尚未通過信箱驗證'
        return render_template('login.html', errorMsg = errorMsg)
    password = cur.fetchone()
    cur.execute(
        'SELECT password FROM members WHERE account = %s', (user_id, )
    )
    password = cur.fetchone()
    if not password:
        errorMsg='<span style="color:#35858B"></span><i class="fa fa-exclamation-triangle" aria-hidden="true"></i>您輸入的帳號不存在'
        return render_template('login.html', errorMsg = errorMsg)
    password = password[0]
    if user_password != password:
        errorMsg='<span style="color:#35858B"></span><i class="fa fa-exclamation-triangle" aria-hidden="true"></i>您輸入的帳號或密碼有誤'
        return render_template('login.html', errorMsg = errorMsg)
    user = User()
    user.id = user_id
    login_user(user)
    return redirect(request.args.get("next") or url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(request.args.get("next") or url_for('index'))

if __name__ == '__main__':
    app.run(debug = True, port = 5000)
