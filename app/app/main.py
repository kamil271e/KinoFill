from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus
from flask_fontawesome import FontAwesome
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField, EmailField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Length

app = Flask(__name__)
fa = FontAwesome(app)
app.secret_key = '123'
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://postgres:{quote_plus('Welcome1@')}@localhost/Filmweb2"
# app.config['UPLOAD_FOLDER'] = "static/images/"
db = SQLAlchemy(app)

global today
today = date.today().strftime("%d.%m.%Y")

class User(db.Model):
    __tablename__ = "users"
    __table_args__ = {'quote': False, 'schema': "filmweb"}

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(5))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __init__(self, login, password_hash, role):
        self.login = login
        self.password_hash = password_hash
        self.role = role

class RegisterForm(FlaskForm):
    login = StringField("Login", validators=[DataRequired(), Length(6, 16)])
    password = PasswordField("Hasło", validators=[DataRequired(), Length(6, 16)])
    role = SelectField("Rola", choices=["Widz", "Dziennikarz", "Wytwórnia filmowa"])
    submit = SubmitField("Zarejestruj")

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html', today=today)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and request.form.get("login") == "admin":
        return redirect(url_for('user', name='admin'))
    elif request.method == 'POST':
        print(request.form['login'])
        login = request.form['login']
        # user = User(login)
        # db.session.add(user)
        # db.session.commit()
    return render_template('login.html', today=today)

@app.route('/register', methods=['GET', 'POST'])
def register():
    login = None
    form = RegisterForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter(User.login == form.login.data).first()
        if user is None: #user doesn't exist
            hashed_password = generate_password_hash(form.password.data, "sha256")
            val = form.role.data
            val = "user" if val == "Widz" else "dev"
            user = User(form.login.data, hashed_password, val)
            # print(User.query.get(current_user, login))
            db.session.add(user)
            db.session.commit()
            flash("Poprawnie zarejestrowano użytkownika")
            # return redirect(url_for("developer_details_change", login=form.login.data))
            return redirect(url_for("login"))
        else:
            flash("Użytkownik o podanym loginie istnieje")
        login = form.login.data
        form.login.data = ''
        form.password.data = ''
    return render_template('register.html', login=login, form=form, today=today)

@app.route('/user/<name>')
def user(name):
    return '<h1>Hello, %s!</h1>' % name

if __name__ == '__main__':
    with app.app_context(): #Flask-SQLAlchemy 3.0 all access to db.engine (and db.session) requires an active Flask application context
        # db.drop_all()
        db.create_all()
    app.run(debug=True)
