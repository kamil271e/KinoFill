from models import *
from forms import *

@login_manager.user_loader # user loader tells Flask-Login how to find a specific user from the ID that is stored in their session cookie
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return Users.query.get(int(user_id))

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html', today=today)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = db.session.query(Users).filter(Users.login == request.form['login']).first()
        if user:
            check = check_password_hash(user.password_hash, request.form['password'])
            if check:
                login_user(user)
                flash("Poprawnie zalogowano użytkownika")
                return redirect(url_for("user"))
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
        user = db.session.query(Users).filter(Users.login == form.login.data).first()
        if user is None: #user doesn't exist
            hashed_password = generate_password_hash(form.password.data, "sha256")
            is_public = ""
            if form.role.data == "Widz":
                role = "v"  # viewer
                if form.viewer_role.data == "Prywatne":
                    is_public = "f"
                else:
                    is_public = "t"
            elif form.role.data == "Dziennikarz":
                role = "j"  # journalist
            elif form.role.data == "Wytwórnia filmowa":
                role = "s"  # studio

            command = f"CALL filmweb.newuser(" \
                      f"'{form.login.data}', " \
                      f"'{hashed_password}', " \
                      f"'{today}', " \
                      f"'{form.user_desc.data}', " \
                      f"'t', " \
                      f"'{role}', " \
                      f"'{form.name.data}', " \
                      f"NULL, " \
                      f"NULL, " \
                      f"NULL, " \
                      f"NULL, " \
                      f"NULL, " \
                      f"'{is_public}'" \
                      f");"
            print(command)
            db.session.execute(command)
            db.session.commit()
            flash("Poprawnie zarejestrowano użytkownika")
            return redirect(url_for("login"))
        else:
            flash("Użytkownik o podanym loginie istnieje")
        login = form.login.data
        form.login.data = ''
        form.password.data = ''
    return render_template('register.html', login=login, form=form, today=today)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Poprawnie wylogowano użytkownika")
    return redirect(url_for("home"))

@app.route('/user')
@login_required # protect from not logged users
def user():
    return render_template('user.html', name=current_user.login, today=today)

@app.route('/list')
@login_required
def list_objects():
    return render_template('list_of_objects.html', today=today)

if __name__ == '__main__':
    # with app.app_context(): #Flask-SQLAlchemy 3.0 all access to db.engine (and db.session) requires an active Flask application context
        # db.drop_all()
        # db.create_all()
    app.run(debug=True)
