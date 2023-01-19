from models import *
from forms import *
from utils import *


# user loader tells Flask-Login how to find a specific user from the ID that is stored in their session cookie
@login_manager.user_loader
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
                flash("User successfuly logged in")
                if user.user_type == 's':
                    return redirect(url_for("studio_details", studio_id=user.user_id))
                else:
                    return redirect(url_for("user"))
            else:
                flash("Incorrect password")
        else:
            flash("User with specified login does not exist")
        return redirect(url_for('login'))  # clear input
    return render_template('login.html', today=today)


@app.route('/register', methods=['GET', 'POST'])
def register():
    login = None
    form = RegisterForm()
    if form.validate_on_submit():
        user = db.session.query(Users).filter(Users.login == form.login.data).first()
        if user is None:  # user doesn't exist
            hashed_password = generate_password_hash(form.password.data, "sha256")
            is_public = ""
            existing_name = ""
            if form.role.data == "Viewer":
                role = "w"  # viewer
                if form.viewer_role.data == "Private":
                    is_public = "f"
                    form.name.data = 'NULL'
                else:
                    is_public = "t"
                    viewer = db.session.query(Viewer).filter(Viewer.nickname == form.name.data).first()
                    if viewer:
                        existing_name = "x"
            elif form.role.data == "Journalist":
                role = "d"  # journalist
                journalist = db.session.query(Journalist).filter(Journalist.nickname == form.name.data).first()
                if journalist:
                    existing_name = "x"
            elif form.role.data == "Studio":
                role = "s"  # studio
                studio = db.session.query(Studio).filter(Studio.name == form.name.data).first()
                if studio:
                    existing_name = "x"

            if form.name.data != 'NULL':
                form.name.data = f"'{form.name.data}'"

            if existing_name == "":
                command = f"CALL filmweb.newuser(" \
                          f"'{form.login.data}', " \
                          f"'{hashed_password}', " \
                          f"'{today}', " \
                          f"'{form.user_desc.data}', " \
                          f"'t', " \
                          f"'{role}', " \
                          f"{form.name.data}, " \
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
                flash("User successfuly registered")
                return redirect(url_for("login"))
            else:
                flash("User with specified username already exists. Choose different one.")
                form.name.data = ''
        else:
            flash("User with specified login already exists. Choose different one.")
            form.login.data = ''
            form.password.data = ''
        login = form.login.data
    return render_template('register.html', login=login, form=form, today=today)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("User successfully logged out")
    return redirect(url_for("home"))


@app.route('/user')
@login_required  # protect from not logged users
def user():
    return render_template('user.html', name=current_user.login, today=today)


@app.route('/list')
def list_objects():
    studios = db.session.query(Studio)
    movies = db.session.query(Movie)
    series = db.session.query(Series)
    actors = db.session.query(Actor)
    directors = db.session.query(Director)
    journalists = db.session.query(Journalist)
    return render_template('list_of_objects.html', today=today, studios=studios, movies=movies, series=series,
                           actors=actors, directors=directors, journalists=journalists)


@app.route('/add_director', methods=['POST', 'GET'])  # access only for studio - role_required
@login_required
def add_director():
    if current_user.user_type not in ['s', 'a']:  # 'a' - 'admin'
        return redirect(url_for("home"))
    if current_user.user_type == 's':  # Studio will not have option to add anything related to a different studio
        choose_studio = False
    else:
        choose_studio = True  # Admin can choose to which studio assign the director
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
            flash("Director successfuly added")
            return redirect(url_for("home"))
        else:
            flash("This director has already been added to the database")
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
                hidden_form = role_form + '_h'
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
            flash("Movie successfuly added")
            return redirect(url_for("home"))
        else:
            flash("This movie has already been added to the database")
    return render_template('add_movie.html', today=today, form=form,
                           genres_options=getGenres(), actors_options=getActors())


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
                hidden_form = role_form + '_h'
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
            flash("Series successfuly added")
            return redirect(url_for("home"))
        else:
            flash("This series has already been added to the database")
    return render_template('add_series.html', today=today, form=form,
                           genres_options=getGenres(), actors_options=getActors())


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
            flash("Actor successfuly added")
            return redirect(url_for("home"))
        else:
            flash("This director has already been added to the database")
    return render_template('add_actor.html', today=today, form=form)


@app.route('/movie_details/<movie_id>')
@login_required
def movie_details(movie_id):
    movie = db.session.query(Movie).filter(Movie.movie_id == movie_id).first()
    studio = db.session.query(Studio).filter(Studio.studio_id == movie.studio_id).first()
    director = db.session.query(Director).filter(Director.director_id == movie.director_id).first()
    genres = db.session.query(Movie_genres).filter(Movie_genres.movie_id == movie_id)
    genres_str = ''  # convert genres query to string
    for genre in genres:
        genres_str += ', ' + genre.genre
    genres_str = genres_str[2:]
    return render_template('movie_details.html', today=today, movie=movie, genres=genres_str,
                           director=director, studio=studio)


@app.route('/studio_details/<studio_id>')
@login_required
def studio_details(studio_id):
    studio = db.session.query(Studio).filter(Studio.studio_id == studio_id).first()
    if studio:
        movies = db.session.query(Movie).filter(Movie.studio_id == studio_id)
        series = db.session.query(Series).filter(Series.studio_id == studio_id)
        actors = db.session.query(Actor).filter(Actor.studio_id == studio_id)
        directors = db.session.query(Director).filter(Director.studio_id == studio_id)
        int_sid = int(studio_id)
    else:
        flash('This studio does not exists')
        return redirect(url_for("home"))
    return render_template('studio_details.html', today=today, studio=studio, movies=movies,
                           series=series, actors=actors, directors=directors, int_sid=int_sid)


@app.route('/director_details/<director_id>')
def director_details(director_id):
    director = db.session.query(Director).filter(Director.director_id == director_id).first()
    studio = db.session.query(Studio).filter(Studio.studio_id == director.studio_id).first()
    movies = db.session.query(Movie).filter(Movie.director_id == director_id)
    series = db.session.query(Series).filter(Series.director_id == director_id)
    return render_template('director_details.html', today=today, director=director,
                           studio=studio, movies=movies, series=series)


@app.route('/studio_change', methods=['GET', 'POST'])
@login_required
def studio_change():
    studio = db.session.query(Studio).filter(Studio.studio_id == current_user.user_id).first()
    form = ChangeStudio(name=studio.name, country=studio.country, creation_date=studio.creation_date)
    if form.validate_on_submit():
        existing_studio = db.session.query(Studio).filter(Studio.name == form.name.data).first()
        if existing_studio and form.name.data != studio.name:
            flash("Studio name already exists. Please enter different name.")
        else:
            print(form.name.data)
            studio.name = form.name.data
            studio.country = form.country.data
            studio.creation_date = form.creation_date.data
            db.session.commit()
            flash("Studio information updated")
            return redirect(url_for("studio_details", studio_id=studio.studio_id))
    return render_template('studio_change.html', today=today, form=form, studio=studio)


@app.route('/add_review/<reviewer_type>/<reviewer_id>', defaults={'object_type': None, 'object_id': None})
@app.route('/add_review/<reviewer_type>/<reviewer_id>/<object_type>/<object_id>')
@login_required
def add_review(reviewer_type, reviewer_id, object_type, object_id):
    # TODO: check if this user wrote a review to this object earlier
    print(reviewer_type, reviewer_id, object_type, object_id)
    if reviewer_type == 'w':
        viewer = db.session.query(Viewer).filter(Viewer.viewer_id == reviewer_id).first()
    elif reviewer_type == 'd':
        journalist = db.session.query(Journalist).filter(Journalist.journalist_id == reviewer_id).first()
    else:
        flash('Review can be added only by viewer and journalist')
        return redirect(url_for("home"))

    movie = None
    series = None
    actor = None
    movies = db.session.query(Movie)
    seriess = db.session.query(Studio)
    actors = db.session.query(Actor)

    if object_type == 'm':
        if object_id:
            movie = db.session.query(Movie).filter(Movie.movie_id == object_id).first()
        form = AddReview(review_object_type="Movie")
    elif object_type == 's':
        if object_id:
            series = db.session.query(Studio).filter(Studio.studio_id == object_id).first()
        form = AddReview(review_object_type="Series")
    elif object_type == 'a':
        if object_id:
            actor = db.session.query(Actor).filter(Actor.actor_id == object_id).first()
        form = AddReview(review_object_type="Actor")
    else:
        form = AddReview()

    # TODO: Add review to database after submit btn

    return render_template('add_review.html', today=today, form=form,
                           movie=movie, series=series, actor=actor,
                           movies=movies, seriess=seriess, actors=actors)


if __name__ == '__main__':
    # Flask-SQLAlchemy 3.0 all access to db.engine (and db.session) requires an active Flask application context
    with app.app_context():
        initGenres()
        # db.drop_all()
        # db.create_all()
    app.run(debug=True)
