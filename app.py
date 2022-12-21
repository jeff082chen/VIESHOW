from flask import *
# from api import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/theater')
def theater():
    return render_template('theater.html')

@app.route('/cineplex')
def cineplex():
    return render_template('cineplex.html')

@app.route('/movies')
def movies():
    return render_template('movies.html')

@app.route('/movieintro')
def movieintro():
    return render_template('movieintro.html')

if __name__ == '__main__':
    app.run(debug = True, port = 5000)
