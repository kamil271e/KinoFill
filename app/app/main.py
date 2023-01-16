from models import *
from forms import *
from utils import *

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
            existing_name = ""
            if form.role.data == "Widz":
                role = "v"  # viewer
                if form.viewer_role.data == "Prywatne":
                    is_public = "f"
                else:
                    is_public = "t"
                    viewer = db.session.query(Viewer).filter(Viewer.nickname == form.name.data).first()
                    if viewer:
                        existing_name = "x"
            elif form.role.data == "Dziennikarz":
                role = "j"  # journalist
                journalist = db.session.query(Journalist).filter(Journalist.nickname == form.name.data).first()
                if journalist:
                    existing_name = "x"
            elif form.role.data == "Wytwórnia filmowa":
                role = "s"  # studio
                studio = db.session.query(Studio).filter(Studio.name == form.name.data).first()
                if studio:
                    existing_name = "x"

            if existing_name == "":
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
                flash("Użytkownik o podanej nazwie istnieje. Wprowadź inną nazwę")
                form.name.data = ''
        else:
            flash("Użytkownik o podanym loginie istnieje")
            form.login.data = ''
            form.password.data = ''
        login = form.login.data
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
    studios = db.session.query(Studio)
    movies = db.session.query(Movie)
    series = db.session.query(Series)
    actors = db.session.query(Actor)
    return render_template('list_of_objects.html', today=today, studios=studios, movies=movies, series=series, actors=actors)

@app.route('/add_director', methods=['POST', 'GET']) #access only for studio - role_required
@login_required
def add_director():
    if current_user.user_type not in ['s', 'a']: # 'a' - 'admin'
        return redirect(url_for("home"))
    if current_user.user_type == 's': # Studio will not have option to add anything related to a different studio
        choose_studio = False
    else: 
        choose_studio = True # Admin can choose to which studio assign the director
    form = AddDirector(choose_studio=choose_studio)
    form.studio.choices = getStudios()
    if form.validate_on_submit():
        director = db.session.query(Director).filter(
            Director.firstname == form.firstname.data,
            Director.surname == form.surname.data,
            Director.birth_date == form.birth_date.data).first()
        if director is None:
            if choose_studio:
                stud_id = form.studio.data
            else:
                stud_id = current_user.user_id
            director = Director(
                firstname=form.firstname.data,
                surname=form.surname.data,
                birth_date=form.birth_date.data,
                country=form.country.data,
                rate=None,
                studio_id=stud_id)
            db.session.add(director)
            db.session.commit()
            flash("Dodano reżysera")
            return redirect(url_for("home"))
        else:
            flash("Ten reżyser został już dodany do bazy danych")
    return render_template('add_director.html', today=today, form=form)

@app.route('/add_movie', methods=['POST', 'GET'])
@login_required
def add_movie():
    if current_user.user_type not in ['s', 'a']:
        return redirect(url_for("home"))
    if current_user.user_type == 's':
        choose_studio = False
    else: 
        choose_studio = True 
    form = AddMovie(choose_studio=choose_studio)
    form.studio.choices = getStudios()
    form.director.choices = getDirectors()
    if form.validate_on_submit():
        if form.redirect_add_director.data:
            return redirect(url_for("add_director"))
        movie = db.session.query(Movie).filter(
            Movie.name == form.name.data,
            Movie.creation_year == form.creation_year.data
        ).first()
        if movie is None:
            if choose_studio:
                stud_id = form.studio.data
            else:
                stud_id = current_user.user_id
            movie = Movie(
                name=form.name.data,
                creation_year=form.creation_year.data,
                length=form.length.data,
                viewers_rating=None,
                studio_id=stud_id,
                director_id=form.director.data        
            )
            db.session.add(movie)
            db.session.commit()
            genres = request.form.getlist("genre")
            for genre in genres:
                movie_genre = Movie_genres(
                    movie_id=movie.get_id(),
                    genre=genre
                )
                db.session.add(movie_genre)
            db.session.commit()

            for i in range(10):
                role_form = 'actor_' + str(i)
                hidden_form = role_form +'_h'
                actor_id = request.form.get(hidden_form)
                character_name = request.form.get(role_form)
                if not actor_id or not character_name:
                    break
                movie_character = Movie_character(
                    character_name=character_name,
                    movie_id=movie.get_id(),
                    actor_id=actor_id
                )
                db.session.add(movie_character)

            db.session.commit()
            flash("Dodano film")
            return redirect(url_for("home"))
        else:
            flash("Ten film został już dodany do bazy danych")
    return render_template('add_movie.html', today=today, form=form, genres_options=getGenres(), actors_options=getActors())

@app.route('/add_series', methods=['POST', 'GET'])
@login_required
def add_series():
    if current_user.user_type not in ['s', 'a']:
        return redirect(url_for("home"))
    if current_user.user_type == 's':
        choose_studio = False
    else: 
        choose_studio = True 
    form = AddSeries(choose_studio=choose_studio)
    form.studio.choices = getStudios()
    form.director.choices = getDirectors()
    if form.validate_on_submit():
        if form.redirect_add_director.data:
            return redirect(url_for("add_director"))
        series = db.session.query(Series).filter(
            Series.name == form.name.data,
            Series.episodes == form.episodes.data
        ).first()
        if series is None:
            if choose_studio:
                stud_id = form.studio.data
            else:
                stud_id = current_user.user_id
            series = Series(
                name=form.name.data,
                episodes=form.episodes.data,
                seasons=request.form['range'],
                viewers_rating=None,
                studio_id=stud_id,
                director_id=form.director.data
            )
            db.session.add(series)
            db.session.commit()

            genres = request.form.getlist("genre")
            for genre in genres:
                series_genre = Series_genres(
                    series_id=series.get_id(),
                    genre=genre
                )
                db.session.add(series_genre)
            db.session.commit()

            for i in range(10):
                role_form = 'actor_' + str(i)
                hidden_form = role_form +'_h'
                actor_id = request.form.get(hidden_form)
                character_name = request.form.get(role_form)
                if not actor_id or not character_name:
                    break
                series_character = Series_character(
                    character_name=character_name,
                    series_id=series.get_id(),
                    actor_id=actor_id
                )
                db.session.add(series_character)
            
            db.session.commit()
            flash("Dodano serial")
            return redirect(url_for("home"))
        else:
            flash("Ten serial został już dodany do bazy danych")
    return render_template('add_series.html', today=today, form=form, genres_options=getGenres(), actors_options=getActors())

@app.route('/add_actor', methods=['POST', 'GET'])
@login_required
def add_actor():
    if current_user.user_type not in ['s', 'a']:
        return redirect(url_for("home"))
    if current_user.user_type == 's':
        choose_studio = False
    else: 
        choose_studio = True 
    form = AddActor(choose_studio=choose_studio)
    form.studio.choices = getStudios()
    if form.validate_on_submit():
        actor = db.session.query(Actor).filter(
            Actor.firstname == form.firstname.data,
            Actor.surname == form.surname.data,
            Actor.birth_date == form.birth_date.data).first()
        if actor is None:
            if choose_studio:
                stud_id = form.studio.data
            else:
                stud_id = current_user.user_id
            actor = Actor(
                firstname=form.firstname.data,
                surname=form.surname.data,
                birth_date=form.birth_date.data,
                country=form.country.data,
                rate=None,
                studio_id=stud_id)
            db.session.add(actor)
            db.session.commit()
            flash("Dodano aktora")
            return redirect(url_for("home"))
        else:
            flash("Ten aktor został już dodany do bazy danych")
    return render_template('add_actor.html', today=today, form=form)

if __name__ == '__main__':
    # with app.app_context(): #Flask-SQLAlchemy 3.0 all access to db.engine (and db.session) requires an active Flask application context
        # db.drop_all()
        # db.create_all()
    app.run(debug=True)
