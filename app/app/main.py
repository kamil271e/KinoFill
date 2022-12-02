from models import *
from forms import *

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html', today=today)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = db.session.query(User).filter(User.login == request.form['login']).first()
        if user:
            check = check_password_hash(user.password_hash, request.form['password'])
            if check:
                # login_user(user)
                flash("Poprawnie zalogowano użytkownika")
                return redirect(url_for('home'))
            else:
                flash("Podano błędne hasło")
        else:
            flash("Użytkownik o podanym loginie nie istnieje")
        return redirect(url_for('login'))  # clear input
    return render_template('login.html', today=today)

@app.route('/register', methods=['GET', 'POST'])
def register():
    login = None
    form = RegisterForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter(User.login == form.login.data).first()
        if user is None: #user doesn't exist
            hashed_password = generate_password_hash(form.password.data, "sha256")
            if form.role.data == "Widz":
                val = "v"  # viewer
            elif form.role.data == "Dziennikarz":
                val = "j"  # journalist
            elif form.role.data == "Wytwórnia filmowa":
                val = "s"  # studio
            else:
                val = ""
            if form.user_desc.data:
                user = User(form.login.data, hashed_password, today, val, form.user_desc.data)
            else:
                user = User(form.login.data, hashed_password, today, val)
            # print(User.query.get(current_user, login))
            db.session.add(user)
            db.session.commit()
            flash("Poprawnie zarejestrowano użytkownika")
            # https://codepen.io/astrit/pen/OJPyqyx
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
