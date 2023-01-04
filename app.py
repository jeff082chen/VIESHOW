import os
import hashlib
import datetime
import copy
import pymysql
from flask import *
from flask_login import *
from flask_wtf import FlaskForm
from wtforms import SelectField
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import api

app = Flask(__name__)
app.secret_key = "12345678" #os.urandom(16).hex()

class CinemasForm(FlaskForm):
    cinemas = SelectField('cinemas')

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

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(minutes=30)

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
    all_cinema = api.get_all_cinemas_name(db = get_db())
    form = CinemasForm()
    form.cinemas.choices = [(i[0], i[0]) for i in all_cinema]
    form.cinemas.default = all_cinema[0]
    form.process()

    db = get_db()
    with db.cursor() as cursor:
        command = f'SELECT * FROM `movie` WHERE `movie_cinema` = "{all_cinema[0][0]}";'
        try:
            cursor.execute(command)
            result = cursor.fetchone()
        except:
            db.rollback()

    initial = list(result)

    return render_template('index.html', form = form, initial = initial)

@app.route('/movie_choice')
def movie_choice():
    cinema = request.args.get('cinema')
    db = get_db()
    with db.cursor() as cursor:
        command = f'SELECT `movie_name` FROM `movie` WHERE `movie_cinema` = "{cinema}";'
        try:
            cursor.execute(command)
            result = cursor.fetchall()
        except:
            db.rollback()

    return jsonify({'movies': list(set(result))})

@app.route('/date_choice')
def date_choice():
    cinema = request.args.get('cinema')
    movie = request.args.get('movie')
    db = get_db()
    with db.cursor() as cursor:
        command = f'SELECT `movie_date` FROM `movie` WHERE `movie_cinema` = "{cinema}" AND `movie_name` = "{movie}";'
        try:
            cursor.execute(command)
            result = cursor.fetchall()
        except:
            db.rollback()

    return jsonify({'dates': sorted(list(set(result)), key = lambda x: datetime.datetime.strptime(x[0], '%Y/%m/%d'))})

@app.route('/time_choice')
def time_choice():
    cinema = request.args.get('cinema')
    movie = request.args.get('movie')
    date = request.args.get('date')
    db = get_db()
    with db.cursor() as cursor:
        command = f'SELECT `movie_ses`, `movie_time` FROM `movie` WHERE `movie_cinema` = "{cinema}" AND `movie_name` = "{movie}" AND `movie_date` = "{date}";'
        try:
            cursor.execute(command)
            result = cursor.fetchall()
        except:
            db.rollback()
    return jsonify({'times': list((result))})

@app.route('/seat')
def seat():
    ID = request.args.get('ID')
    info = api.get_session_info(ID, db = get_db())
    empty_seats = api.get_empty_seats(ID, db = get_db())
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    columns = [str(col) for col in range(1, 11)]
    return render_template('seat.html', info = info, empty_seats = empty_seats, rows = rows, columns = columns)

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
    movie_eng_name = {movie_info[0]: api.get_movie_englishname(movie_info[0], db = get_db())[0] for movie_info in movie_list}
    versions = list(set(sessions_info['movie_version']))
    version_dict = {version: copy.deepcopy([]) for version in versions}
    movie_dict = {movie: copy.deepcopy(version_dict) for movie in movie_list}
    dates_dict = {date: copy.deepcopy(movie_dict) for date in dates}
    for i in range(len(sessions_info['movie_cinema'])):
        dates_dict[sessions_info['movie_date'][i]][sessions_info['movie_info'][i]][sessions_info['movie_version'][i]].append(sessions_info['movie_time'][i])
        dates_dict[sessions_info['movie_date'][i]][sessions_info['movie_info'][i]][sessions_info['movie_version'][i]].sort(key = lambda x: datetime.datetime.strptime(x[0], '%H:%M'))
    return render_template('cineplex.html', info = info, sessions = dates_dict, dates = dates, movies = movie_list, versions = versions, movie_eng_name = movie_eng_name)

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
    validated = api.member_is_valid(user_id, db = get_db())
    if validated is None:
        errorMsg='<span style="color:#35858B"></span><i class="fa fa-exclamation-triangle" aria-hidden="true"></i>此帳號不存在'
        return render_template('login.html', errorMsg = errorMsg)
    if validated[0] == False:
        errorMsg='<span style="color:#35858B"></span><i class="fa fa-exclamation-triangle" aria-hidden="true"></i>此帳號尚未通過信箱驗證'
        return render_template('login.html', errorMsg = errorMsg)
    password = api.get_member_password(user_id, db = get_db())
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
    return redirect(url_for('index')) # request.args.get("next") or 

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index')) # request.args.get("next") or 

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template("register.html")
    name = request.form['name']
    birthday = request.form['birthday']
    phone = request.form['phone']
    email = request.form['email']

    password = api.get_member_password(email, db = get_db())
    if password:
        errorMsg='<span style="color:#35858B"></span><i class="fa fa-exclamation-triangle" aria-hidden="true"></i>您輸入的帳號已存在'
        return render_template('register.html', errorMsg = errorMsg)

    creditcard = request.form['creditcard']
    password = request.form['password']
    password_confirmation = request.form['password_confirmation']
    if password_confirmation != password:
        errorMsg='<span style="color:#35858B"></span><i class="fa fa-exclamation-triangle" aria-hidden="true"></i>您輸入的密碼有誤'
        return render_template('register.html', errorMsg = errorMsg)
    password += salt
    password = hashlib.sha256(password.encode()).hexdigest()
    verification_code = os.urandom(5).hex()
    api.create_new_member(email, password, name, email, phone, birthday, creditcard, verification_code, db = get_db())

    content = MIMEMultipart()  #建立MIMEMultipart物件
    content["subject"] = f"VIESHOW 信箱驗證"  #郵件標題
    content["from"] = "VIESHOW0000@gmail.com"  #寄件者
    content["to"] = email #收件者
    content.attach(MIMEText(f"您的信箱驗證碼為：{verification_code}\n驗證網址：http://127.0.0.1:5000/verification\n"))  #郵件內容

    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            # qwcmzdsooaygmoac
            smtp.login("VIESHOW0000@gmail.com", "beztvmozbulzijru")  # 登入寄件者gmail
            smtp.send_message(content)  # 寄送郵件
            print("Complete!")
        except Exception as e:
            print("Error message: ", e)

    return redirect(url_for('index'))

@app.route('/verification', methods=['GET', 'POST'])
def verification():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template("verification.html")
    email = request.form['email']
    password = request.form['password']
    verification_code = request.form['verification_code']
    if verification_code != api.get_member_verification_code(email, db = get_db())[0]:
        errorMsg='<span style="color:#35858B"></span><i class="fa fa-exclamation-triangle" aria-hidden="true"></i>您輸入的驗證碼有誤'
        return render_template('verification.html', errorMsg = errorMsg)
    api.verify_member(email, db = get_db())
    return render_template('login.html')

@app.route('/member_service')
@login_required
def member_service():
    return render_template('member_service.html')

@app.route('/profile')
@login_required
def profile():
    info = api.get_member_info(current_user.id, db = get_db())
    return render_template('profile.html', info = info)

@app.route('/recharge', methods = ['POST'])
@login_required
def reincharge():
    point = int(request.form['point'])
    point += point // 10

    db = get_db()
    with db.cursor() as cursor:
        
        try:
            command = f'UPDATE member SET mem_point = mem_point + {point} WHERE account = "{current_user.id}";'
            cursor.execute(command)
            db.commit()
        except:
            db.rollback()

        cursor.close()
    return redirect(url_for('profile'))

@app.route('/change_info', methods = ['POST'])
@login_required
def change_info():
    phone = request.form['phone']
    birthday = request.form['birthday']

    db = get_db()
    with db.cursor() as cursor:
        
        try:
            if phone:
                command = f'UPDATE member SET mem_phone = "{phone}" WHERE account = "{current_user.id}";'
                cursor.execute(command)
                db.commit()
            if birthday:
                command = f'UPDATE member SET mem_birthday = "{birthday}" WHERE account = "{current_user.id}";'
                cursor.execute(command)
                db.commit()
        except:
            db.rollback()

        cursor.close()
    return redirect(url_for('profile'))

@app.route('/forget_password', methods=['GET', 'POST'])
def forget_password():

    if request.method == 'GET':
        return render_template('forget_password.html')

    account = request.form.get('account')

    random_password = os.urandom(5).hex()

    content = MIMEMultipart()  #建立MIMEMultipart物件
    content["subject"] = f"VIESHOW 重置密碼"  #郵件標題
    content["from"] = "VIESHOW0000@gmail.com"  #寄件者
    content["to"] = account #收件者
    content.attach(MIMEText(f"您的新密碼為：{random_password}\n"))  #郵件內容

    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            # qwcmzdsooaygmoac
            smtp.login("VIESHOW0000@gmail.com", "beztvmozbulzijru")  # 登入寄件者gmail
            smtp.send_message(content)  # 寄送郵件
            print("Complete!")
        except Exception as e:
            print("Error message: ", e)

    random_password += salt
    random_password = hashlib.sha256(random_password.encode()).hexdigest()

    db = get_db()
    with db.cursor() as cursor:
            
        try:
            command = f'UPDATE member SET password = "{random_password}" WHERE account = "{account}";'
            cursor.execute(command)
            db.commit()
        except:
            db.rollback()

        cursor.close()

    logout_user()
    return redirect(url_for('login'))

@app.route('/change_password', methods = ['POST'])
@login_required
def change_password():
    password = request.form['password']
    new_password = request.form['new_password']
    password_check = request.form['password_check']

    original_password = api.get_member_password(current_user.id, db = get_db())[0]
    password += salt
    password = hashlib.sha256(password.encode()).hexdigest()

    if password_check != new_password or password != original_password:
        info = api.get_member_info(current_user.id, db = get_db())
        password_errorMsg='<span style="color:#35858B"></span><i class="fa fa-exclamation-triangle" aria-hidden="true"></i>您輸入的密碼有誤'
        return render_template('profile.html', info = info, password_errorMsg = password_errorMsg)

    new_password += salt
    new_password = hashlib.sha256(new_password.encode()).hexdigest()

    db = get_db()
    with db.cursor() as cursor:
        
        try:
            command = f'UPDATE member SET password = "{new_password}" WHERE account = "{current_user.id}";'
            cursor.execute(command)
            db.commit()
        except:
            db.rollback()

        cursor.close()
    return redirect(url_for('profile'))

@app.route('/change_email', methods=['POST'])
@login_required
def change_email():
    email = request.form['email']

    if email == current_user.id:
        info = api.get_member_info(current_user.id, db = get_db())
        email_errorMsg='<span style="color:#35858B"></span><i class="fa fa-exclamation-triangle" aria-hidden="true"></i>您輸入的帳號和原先相同'
        return render_template('profile.html', info = info, email_errorMsg = email_errorMsg)

    password = api.get_member_password(email, db = get_db())
    if password:
        info = api.get_member_info(current_user.id, db = get_db())
        email_errorMsg='<span style="color:#35858B"></span><i class="fa fa-exclamation-triangle" aria-hidden="true"></i>您輸入的帳號已存在'
        return render_template('profile.html', info = info, email_errorMsg = email_errorMsg)

    verification_code = os.urandom(5).hex()

    db = get_db()
    with db.cursor() as cursor:
        
        try:
            command = f'UPDATE member SET mem_email = "{email}", account = "{email}", mem_veri = "{verification_code}", veri_pass = 0 WHERE account = "{current_user.id}";'
            print(command)
            cursor.execute(command)
            db.commit()
        except:
            print(command)
            db.rollback()

        cursor.close()

    content = MIMEMultipart()  #建立MIMEMultipart物件
    content["subject"] = f"VIESHOW 信箱驗證"  #郵件標題
    content["from"] = "VIESHOW0000@gmail.com"  #寄件者
    content["to"] = email #收件者
    content.attach(MIMEText(f"您的信箱驗證碼為：{verification_code}\n驗證網址：http://127.0.0.1:5000/verification\n"))  #郵件內容

    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            # qwcmzdsooaygmoac
            smtp.login("VIESHOW0000@gmail.com", "beztvmozbulzijru")  # 登入寄件者gmail
            smtp.send_message(content)  # 寄送郵件
            print("Complete!")
        except Exception as e:
            print("Error message: ", e)

    logout_user()
    return redirect(url_for('index'))

@app.route('/order3', methods = ['POST'])
@login_required
def order3():
    session_id = request.form['session_id']
    return render_template('order3.html', session_id = session_id)

@app.route('/book', methods = ['POST'])
@login_required
def book():
    session_id = request.form['session_id']
    ticket_type = request.form['ticket_type']
    type_str = "一般票種" if ticket_type == 'general' else "優惠套票"
    if type_str == "一般票種":
        ticket_info = {
            'name': "全票",
            'price': 360
        }
    else:
        ticket_info = {
            'name': "優惠票",
            'price': 340
        }
    meals = {
        ('drink', '飲料類'): {
            ('large', '大可樂'): 64,
            ('medium', '中可樂'): 55,
            ('small', '小可樂'): 51
        },
        ('popcorn', '爆米花類'): {
            ('large', '大爆米花'): 123,
            ('medium', '中爆米花'): 115,
            ('small', '小爆米花'): 106
        }
    }
    session_info = api.get_session_info(session_id, db = get_db())
    movie_eng_name = api.get_movie_englishname(session_info[1], db = get_db())
    return render_template('book.html', info = session_info, type_str = type_str, ticket_info = ticket_info, meals = meals, session_id = session_id, ticket_type = ticket_type, movie_eng_name = movie_eng_name)

@app.route('/bookseat', methods = ['POST'])
@login_required
def bookseat():
    session_id = request.form['session_id']
    session_info = api.get_session_info(session_id, db = get_db())
    movie_eng_name = api.get_movie_englishname(session_info[1], db = get_db())
    ticket_type = request.form['ticket_type']
    if ticket_type == 'general':
        ticket_info = {
            'name': "全票",
            'price': 360
        }
    else:
        ticket_info = {
            'name': "優惠票",
            'price': 340
        }
    ticket_count = request.form['ticket_count']
    total_price = (ticket_info['price'] + 40) * int(ticket_count)

    meals = {
        'large_drink': int(request.form['drink_large']),
        'medium_drink': int(request.form['drink_medium']),
        'small_drink': int(request.form['drink_small']),
        'large_popcorn': int(request.form['popcorn_large']),
        'medium_popcorn': int(request.form['popcorn_medium']),
        'small_popcorn': int(request.form['popcorn_small'])
    }

    empty_seats = api.get_empty_seats(session_id, db = get_db())
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    columns = [str(col) for col in range(1, 11)]
    return render_template('bookseat.html', info = session_info, empty_seats = empty_seats, rows = rows, columns = columns, ticket_count = ticket_count, ticket_info = ticket_info, total_price = total_price, ticket_type = ticket_type, session_id = session_id, meals = meals, movie_eng_name = movie_eng_name)

@app.route('/check_order', methods = ['POST'])
@login_required
def check_order():
    session_id = request.form['session_id']
    session_info = api.get_session_info(session_id, db = get_db())
    movie_eng_name = api.get_movie_englishname(session_info[1], db = get_db())
    cinema_eng_name = api.get_studio_englishname(session_info[3], db = get_db())

    ticket_type = request.form['ticket_type']
    if ticket_type == 'general':
        ticket_info = {
            'name': "全票",
            'price': 360
        }
    else:
        ticket_info = {
            'name': "優惠票",
            'price': 340
        }
    ticket_count = request.form['ticket_count']
    total_price = (ticket_info['price'] + 40) * int(ticket_count)

    empty_seats = api.get_empty_seats(session_id, db = get_db())
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    columns = [str(col) for col in range(1, 11)]

    meals = {
        'large_drink': int(request.form['large_drink']),
        'medium_drink': int(request.form['medium_drink']),
        'small_drink': int(request.form['small_drink']),
        'large_popcorn': int(request.form['large_popcorn']),
        'medium_popcorn': int(request.form['medium_popcorn']),
        'small_popcorn': int(request.form['small_popcorn'])
    }

    all_seats = [v for k, v in request.form.items() if k.startswith('seat_')]
    for seat in all_seats:
        if not api.seat_available(session_id, seat, db = get_db()):
            errorMsg = f"{seat} is not available, please select another one"
            return render_template('bookseat.html', errorMsg = errorMsg, info = session_info, empty_seats = empty_seats, rows = rows, columns = columns, ticket_count = ticket_count, ticket_info = ticket_info, total_price = total_price, ticket_type = ticket_type, session_id = session_id, meals = meals, movie_eng_name = movie_eng_name)
    if len(all_seats) != int(ticket_count):
        errorMsg = f"you need to select {ticket_count} seats"
        return render_template('bookseat.html', errorMsg = errorMsg, info = session_info, empty_seats = empty_seats, rows = rows, columns = columns, ticket_count = ticket_count, ticket_info = ticket_info, total_price = total_price, ticket_type = ticket_type, session_id = session_id, meals = meals, movie_eng_name = movie_eng_name)
    
    all_seats = ", ".join(all_seats)

    total_price += meals['large_drink'] * 64
    total_price += meals['medium_drink'] * 55
    total_price += meals['small_drink'] * 51
    total_price += meals['large_popcorn'] * 123
    total_price += meals['medium_popcorn'] * 115
    total_price += meals['small_popcorn'] * 106

    point = api.get_member_point(current_user.id, db = get_db())
    name = api.get_member_name(current_user.id, db = get_db())

    max_point = min(int(point[0]), total_price)
    return render_template('check_order.html', info = session_info, movie_eng_name = movie_eng_name, cinema_eng_name = cinema_eng_name, ticket_info = ticket_info, total_price = total_price, all_seats = all_seats, point = point, name = name, meals = meals, ticket_type = ticket_type, session_id = session_id, max_point = max_point)

@app.route('/ticket_record', methods = ['GET', 'POST'])
@login_required
def ticket_record():

    if request.method == 'POST':
        api.book_tickets(account = current_user.id, 
            movie_ses = request.form['session_id'], 
            ticket_type = 0 if request.form['ticket_type'] == 'general' else 1, 
            type_price = request.form['total_price'], 
            mem_point = request.form['point'] if request.form['point'] != '' else 0, 
            large_popcorn = request.form['large_popcorn'],
            medium_popcorn = request.form['medium_popcorn'],
            small_popcorn = request.form['small_popcorn'],
            large_drink = request.form['large_drink'],
            medium_drink = request.form['medium_drink'],
            small_drink = request.form['small_drink'],
            seats = request.form['seats'],
            db = get_db()
        )

    records = api.get_booking_history(current_user.id, db = get_db())

    session_infos = {}
    for record in records:
        session_id = record[2]
        session_info = api.get_session_info(session_id, db = get_db())
        movie_eng_name = api.get_movie_englishname(session_info[1], db = get_db())
        cinema_eng_name = api.get_studio_englishname(session_info[3], db = get_db())

        record_id = record[1]
        session_infos[record_id] = {
            'movie_name': session_info[1],
            'cinema_name': session_info[3],
            'movie_eng_name': movie_eng_name[0],
            'cinema_eng_name': cinema_eng_name[0],
            'place': session_info[4],
            'date': session_info[5],
            'time': session_info[6],
            'seats': api.get_booking_seats(record_id, db = get_db())
        }

    return render_template('ticket_record.html', records = records, session_infos = session_infos)

@app.route('/delete_ticket', methods = ['POST'])
@login_required
def delete_ticket():
    ID = request.form['ticket_id']

    db = get_db()
    cursor = db.cursor()

    command = f'SELECT * FROM rec_ticket WHERE ticket_id = {ID};'
    cursor.execute(command)
    info = cursor.fetchone()

    command = f'SELECT `seat` FROM rec_seat WHERE ticket_id = {ID};'
    cursor.execute(command)
    seats = cursor.fetchall()

    command = f'UPDATE `member` SET `mem_point` = `mem_point` + {info[5]} WHERE `account` = "{current_user.id}";'
    cursor.execute(command)
    db.commit()

    for seat in seats:
        command = f'UPDATE `seat` SET `seat_bool` = 0 WHERE `movie_ses` = {info[2]} AND `seat` = "{seat[0]}";'
        print(command)
        cursor.execute(command)
        db.commit()

    command = f'DELETE FROM rec_ticket WHERE ticket_id = {ID};'
    cursor.execute(command)
    db.commit()

    command = f'DELETE FROM rec_seat WHERE ticket_id = {ID};'
    cursor.execute(command)
    db.commit()

    cursor.close()

    return redirect(url_for('ticket_record'))

@app.route('/modifie_booking', methods=['POST'])
@login_required
def modifie_booking():
    ticket_id = request.form['ticket_id']

    db = get_db()
    cursor = db.cursor()
    command = f'SELECT `movie_ses` FROM `rec_ticket` WHERE `ticket_id` = {ticket_id};'
    cursor.execute(command)
    session_id = cursor.fetchone()[0]
    cursor.close()

    session_info = api.get_session_info(session_id, db = get_db())
    movie_eng_name = api.get_movie_englishname(session_info[1], db = get_db())
    meals = {
        ('drink', '飲料類'): {
            ('large', '大可樂'): 64,
            ('medium', '中可樂'): 55,
            ('small', '小可樂'): 51
        },
        ('popcorn', '爆米花類'): {
            ('large', '大爆米花'): 123,
            ('medium', '中爆米花'): 115,
            ('small', '小爆米花'): 106
        }
    }

    return render_template('modifie_booking.html', info = session_info, movie_eng_name = movie_eng_name, meals = meals, ticket_id = ticket_id)

@app.route('/check_modifie', methods = ['POST'])
@login_required
def check_modifie():
    meals = {
        'large_drink': int(request.form['large_drink']),
        'medium_drink': int(request.form['medium_drink']),
        'small_drink': int(request.form['small_drink']),
        'large_popcorn': int(request.form['large_popcorn']),
        'medium_popcorn': int(request.form['medium_popcorn']),
        'small_popcorn': int(request.form['small_popcorn'])
    }

    ticket_id = request.form['ticket_id']

    db = get_db()
    cursor = db.cursor()
    command = f'SELECT `movie_ses`, `ticket_type`, `mem_point` FROM `rec_ticket` WHERE `ticket_id` = {ticket_id};'
    cursor.execute(command)
    result = cursor.fetchone()
    cursor.close()

    session_id = result[0]

    session_info = api.get_session_info(session_id, db = get_db())
    movie_eng_name = api.get_movie_englishname(session_info[1], db = get_db())
    cinema_eng_name = api.get_studio_englishname(session_info[3], db = get_db())

    ticket_type = result[1]
    if ticket_type == 0:
        ticket_info = {
            'name': "全票",
            'price': 360
        }
    else:
        ticket_info = {
            'name': "優惠票",
            'price': 340
        }

    db = get_db()
    cursor = db.cursor()
    command = f'SELECT `seat` FROM `rec_seat` WHERE `ticket_id` = {ticket_id};'
    cursor.execute(command)
    seats = cursor.fetchall()
    all_seats = ", ".join([seat[0] for seat in seats])

    ticket_count = len(seats)
    total_price = (ticket_info['price'] + 40) * int(ticket_count)

    total_price += meals['large_drink'] * 64
    total_price += meals['medium_drink'] * 55
    total_price += meals['small_drink'] * 51
    total_price += meals['large_popcorn'] * 123
    total_price += meals['medium_popcorn'] * 115
    total_price += meals['small_popcorn'] * 106

    point = api.get_member_point(current_user.id, db = get_db())
    name = api.get_member_name(current_user.id, db = get_db())

    current_point = int(point[0]) + int(result[2])
    max_point = min(current_point, total_price)

    return render_template('check_modifie.html', meals = meals, info = session_info, movie_eng_name = movie_eng_name, cinema_eng_name = cinema_eng_name, total_price = total_price, all_seats = all_seats, point = point, name = name, max_point = max_point, current_point = current_point, ticket_info = ticket_info, ticket_id = ticket_id)

@app.route('/modifie', methods = ['POST'])
@login_required
def modifie():
    ticket_id = request.form['ticket_id']
    total_price = request.form['total_price']
    large_popcorn = request.form['large_popcorn']
    medium_popcorn = request.form['medium_popcorn']
    small_popcorn = request.form['small_popcorn']
    large_drink = request.form['large_drink']
    medium_drink = request.form['medium_drink']
    small_drink = request.form['small_drink']
    point = request.form['point']

    db = get_db()
    cursor = db.cursor()
    command = f'SELECT `mem_point` FROM `rec_ticket` WHERE `ticket_id` = {ticket_id};'
    cursor.execute(command)
    current_point = cursor.fetchone()[0]
    cursor.close()

    db = get_db()
    cursor = db.cursor()
    command = f'UPDATE member SET `mem_point` = `mem_point` - {int(point) - int(current_point)} WHERE `account` = "{current_user.id}";'
    cursor.execute(command)
    db.commit()
    cursor.close()

    db = get_db()
    cursor = db.cursor()
    command = f'UPDATE `rec_ticket` SET'
    command += f' `type_price` = {total_price}'
    command += f', `mem_point` = {point}'
    command += f', `large_popcorn` = {large_popcorn}'
    command += f', `medium_popcorn` = {medium_popcorn}'
    command += f', `small_popcorn` = {small_popcorn}'
    command += f', `large_drink` = {large_drink}'
    command += f', `medium_drink` = {medium_drink}'
    command += f', `small_drink` = {small_drink}'
    command +=  f' WHERE `ticket_id` = {ticket_id};'
    cursor.execute(command)
    db.commit()
    cursor.close()

    return redirect(url_for('ticket_record'))

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error = '404 Not Found'), 404

@app.errorhandler(500)
def not_found(e):
    return render_template('error.html', error = '500 Internal Server Error', description = '請聯絡客服尋求進一步的協助'), 500

if __name__ == '__main__':
    app.run(debug = True, port = 5000)
