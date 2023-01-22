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
                flash("User successfully logged in")
                if user.user_type == 's':
                    return redirect(url_for("studio_details", studio_id=user.user_id))
                elif user.user_type == 'd':
                    return redirect(url_for("journalist_details", journalist_id=user.user_id))
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
                name = form.name.data.strip("'")
                if(name == 'NULL'):
                    name = None
                # calling procedure more safely
                command = text("CALL filmweb.newuser(:login, :password, :join_date, :user_desc, :active, :role, :name, :country, :creation_date, :firstname, :surname, :birthdate, :is_public);")
                command = command.bindparams(login=form.login.data, password=hashed_password, join_date=today, user_desc=form.user_desc.data, active='t',
                                role=role, name=name, country=None, creation_date=None, firstname=None, surname=None, birthdate=None, is_public=is_public)
                print(command)
                db.session.execute(command)
                db.session.commit()
                flash("User successfully registered")
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
            flash("Director successfully added")
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
                character_names = request.form.get(role_form)
                if not actor_id or not character_names:
                    break
                names_list = character_names.split(",")
                print(names_list)
                for character_name in names_list:
                    if character_name != ' ' and character_name != '':
                        movie_character = Movie_character(
                            character_name=character_name.lstrip(),
                            movie_id=movie.get_id(),
                            actor_id=actor_id
                        )
                        db.session.add(movie_character)

            db.session.commit()
            flash("Movie successfully added")
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
                character_names = request.form.get(role_form)
                if not actor_id or not character_names:
                    break
                names_list = character_names.split(",")
                for character_name in names_list:
                    if character_name != ' ' and character_name != '':
                        series_character = Series_character(
                            character_name=character_name,
                            series_id=series.get_id(),
                            actor_id=actor_id
                        )
                        db.session.add(series_character)

            db.session.commit()
            flash("Series successfully added")
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
            flash("Actor successfully added")
            return redirect(url_for("home"))
        else:
            flash("This director has already been added to the database")
    return render_template('add_actor.html', today=today, form=form)


@app.route('/movie_details/<movie_id>')
@login_required
def movie_details(movie_id=None):
    movie = db.session.query(Movie).filter(Movie.movie_id == movie_id).first()
    if movie:
        studio = db.session.query(Studio).filter(Studio.studio_id == movie.studio_id).first()
        director = db.session.query(Director).filter(Director.director_id == movie.director_id).first()
        genres = db.session.query(Movie_genres).filter(Movie_genres.movie_id == movie.movie_id)
        genres_str = ''  # convert genres query to string
        for genre in genres:
            genres_str += ', ' + genre.genre
        genres_str = genres_str[2:]
        v_reviews = db.session.query(Review).filter(Review.movie_id == movie_id, Review.author_type == 'w')
        j_reviews = db.session.query(Review).filter(Review.movie_id == movie_id, Review.author_type == 'd')
        viewers = db.session.query(Viewer)
        journalists = db.session.query(Journalist)
        characters = db.session.query(Movie_character).filter(Movie_character.movie_id == movie_id)
        actors=[]
        for character in characters:
            actors.append(db.session.query(Actor).filter(Actor.actor_id == character.actor_id).first())
        actors = list(set(actors))
    else:
        flash("This movie does not exists")
        return redirect(url_for("list_objects"))
    return render_template('movie_details.html', today=today, movie=movie, genres=genres_str,
                           director=director, studio=studio, v_reviews=v_reviews, j_reviews=j_reviews,
                           viewers=viewers, journalists=journalists, characters=characters, actors=actors)


@app.route('/studio_details/<studio_id>')
@login_required
def studio_details(studio_id=None):
    studio = db.session.query(Studio).filter(Studio.studio_id == studio_id).first()
    if studio:
        user = db.session.query(Users).filter(Users.user_id == studio_id).first()
        movies = db.session.query(Movie).filter(Movie.studio_id == studio_id)
        series = db.session.query(Series).filter(Series.studio_id == studio_id)
        actors = db.session.query(Actor).filter(Actor.studio_id == studio_id)
        directors = db.session.query(Director).filter(Director.studio_id == studio_id)
        all_directors = db.session.query(Director)
    else:
        flash('This studio does not exists')
        return redirect(url_for("list_objects"))
    return render_template('studio_details.html', today=today, studio=studio, movies=movies,
                           series=series, actors=actors, directors=directors, user=user,
                           all_directors=all_directors)


@app.route('/director_details/<director_id>')
def director_details(director_id=None):
    director = db.session.query(Director).filter(Director.director_id == director_id).first()
    if director:
        studio = db.session.query(Studio).filter(Studio.studio_id == director.studio_id).first()
        movies = db.session.query(Movie).filter(Movie.director_id == director_id)
        series = db.session.query(Series).filter(Series.director_id == director_id)
    else:
        flash("This director does not exists")
        return redirect(url_for("list_objects"))
    return render_template('director_details.html', today=today, director=director,
                           studio=studio, movies=movies, series=series)


@app.route('/studio_change', methods=['GET', 'POST'])
@login_required
def studio_change():
    studio = db.session.query(Studio).filter(Studio.studio_id == current_user.user_id).first()
    if studio:
        form = ChangeStudio(name=studio.name, country=studio.country, creation_date=studio.creation_date)
        if form.validate_on_submit():
            existing_studio = db.session.query(Studio).filter(Studio.name == form.name.data).first()
            if existing_studio and form.name.data != studio.name:
                flash("Studio name already exists. Please enter different name.")
            else:
                studio.name = form.name.data
                studio.country = form.country.data
                studio.creation_date = form.creation_date.data
                db.session.commit()
                flash("Studio information updated")
                return redirect(url_for("studio_details", studio_id=studio.studio_id))
    else:
        flash('This studio does not exists')
        return redirect(url_for("list_objects"))
    return render_template('studio_change.html', today=today, form=form, studio=studio)


@app.route('/journalist_change', methods=['GET', 'POST'])
@login_required
def journalist_change():
    journalist = db.session.query(Journalist).filter(Journalist.journalist_id == current_user.user_id).first()
    user = db.session.query(Users).filter(Users.user_id == current_user.user_id).first()
    if journalist:
        form = ChangeJournalist(nickname=journalist.nickname, firstname=journalist.firstname, surname=journalist.surname, birth_date=journalist.birth_date, user_desc=user.description)
        if form.validate_on_submit():
            existing_journalist = db.session.query(Journalist).filter(Journalist.nickname == form.nickname.data).first()
            if existing_journalist and form.nickname.data != journalist.nickname:
                flash("Journalist nickname already exists. Please enter different nickname.")
            else:
                journalist.nickname = form.nickname.data
                journalist.firstname = form.firstname.data
                journalist.surname = form.surname.data
                journalist.birth_date = form.birth_date.data
                user.description = form.user_desc.data
                db.session.commit()
                flash("Journalist information updated")
                return redirect(url_for("journalist_details", journalist_id=journalist.journalist_id))
    else:
        flash('This journalist does not exists')
        return redirect(url_for("list_objects"))
    return render_template('journalist_change.html', today=today, form=form, journalist=journalist, user=user)


@app.route('/viewer_change', methods=['GET', 'POST'])
@login_required
def viewer_change():
    viewer = db.session.query(Viewer).filter(Viewer.viewer_id == current_user.user_id).first()
    user = db.session.query(Users).filter(Users.user_id == current_user.user_id).first()
    if viewer:
        form = ChangePublicViewer(nickname=viewer.nickname, user_desc=user.description, viewer_role=user.user_type)
        if form.validate_on_submit():
            existing_viewer = db.session.query(Viewer).filter(Viewer.nickname == form.nickname.data).first()
            if existing_viewer and form.nickname.data != viewer.nickname:
                flash("Viewer nickname already exists. Please enter different nickname.")
            else:
                if form.viewer_role.data == 'Private':
                    user.description = None
                    viewer.is_public = 'f'
                    viewer.nickname = None
                    db.session.commit()
                    flash("User type changed to private")
                    return redirect(url_for('home'))
                else:
                    viewer.is_public = 't'
                    viewer.nickname = form.nickname.data
                    user.description = form.user_desc.data
                    db.session.commit()
                    flash("Viewer information updated")
                    return redirect(url_for("viewer_details", viewer_id=viewer.viewer_id))
    else:
        flash('This viewer does not exists')
        return redirect(url_for("list_objects"))
    return render_template('viewer_change.html', today=today, form=form, viewer=viewer, user=user)


@app.route('/movie_change/<movie_id>', methods=['GET', 'POST'])
@login_required
def movie_change(movie_id=None):
    movie = db.session.query(Movie).filter(Movie.movie_id == movie_id).first()
    if movie:
        form = ChangeMovie(choose_studio=False,name=movie.name, creation_year=movie.creation_year, length=movie.length)
        if form.validate_on_submit():
            existing_movie = db.session.query(Movie).filter(Movie.name == form.name.data, Movie.creation_year == form.creation_year.data).first()
            if existing_movie and form.name.data != movie.name and form.creation_year.data != movie.creation_year:
                flash("This movie already exists. Please enter different data.")
            else:
                movie.name = form.name.data
                movie.creation_year = form.creation_year.data
                movie.length = form.length.data
                db.session.commit()
                flash("Movie information updated")
                return redirect(url_for("movie_details", movie_id=movie.movie_id))
    else:
        flash('This movie does not exists')
        return redirect(url_for("list_objects"))
    return render_template('movie_change.html', today=today, form=form, movie=movie)


@app.route('/series_change/<series_id>', methods=['GET', 'POST'])
@login_required
def series_change(series_id=None):
    series = db.session.query(Series).filter(Series.series_id == series_id).first()
    if series:
        form = ChangeSeries(name=series.name, episodes=series.episodes, seasons=series.seasons)
        if form.validate_on_submit():
            existing_series = db.session.query(Series).filter(Series.name == form.name.data, Series.episodes == form.episodes.data).first()
            if existing_series and form.name.data != series.name and form.episodes.data != series.episodes:
                flash("This series already exists. Please enter different data.")
            else:
                series.name = form.name.data
                series.episodes = form.episodes.data
                series.seasons = form.seasons.data
                db.session.commit()
                flash("Series information updated")
                return redirect(url_for("series_details", series_id=series.series_id))
    else:
        flash('This series does not exists')
        return redirect(url_for("list_objects"))
    return render_template('series_change.html', today=today, form=form, series=series)


@app.route('/actor_change/<actor_id>', methods=['GET', 'POST'])
@login_required
def actor_change(actor_id=None):
    actor = db.session.query(Actor).filter(Actor.actor_id == actor_id).first()
    if actor:
        form = ChangeActor(choose_studio=False, firstname=actor.firstname, surname=actor.surname, birth_date=actor.birth_date, country=actor.country)
        if form.validate_on_submit():
            existing_actor = db.session.query(Actor).filter(Actor.firstname == form.firstname.data, Actor.surname == form.surname.data, Actor.birth_date == form.birth_date.data).first()
            if existing_actor and form.firstname.data != actor.firstname and form.surname.data != actor.surname and form.birth_date.data != actor.birth_date:
                flash("This actor already exists. Please enter different data.")
            else:
                actor.firstname = form.firstname.data
                actor.surname = form.surname.data
                actor.birth_date = form.birth_date.data
                actor.country = form.country.data
                db.session.commit()
                flash("Actor information updated")
                return redirect(url_for("actor_details", actor_id=actor.actor_id))
    else:
        flash('This actor does not exists')
        return redirect(url_for("list_objects"))
    return render_template('actor_change.html', today=today, form=form, actor=actor)


@app.route('/director_change/<director_id>', methods=['GET', 'POST'])
@login_required
def director_change(director_id=None):
    director = db.session.query(Director).filter(Director.director_id == director_id).first()
    if director:
        form = ChangeDirector(choose_studio=False, firstname=director.firstname, surname=director.surname, birth_date=director.birth_date, country=director.country)
        if form.validate_on_submit():
            existing_director = db.session.query(Director).filter(Director.firstname == form.firstname.data, Director.surname == form.surname.data, Director.birth_date == form.birth_date.data).first()
            if existing_director and form.firstname.data != director.firstname and form.surname.data != director.surname and form.birth_date.data != director.birth_date:
                flash("This director already exists. Please enter different data.")
            else:
                director.firstname = form.firstname.data
                director.surname = form.surname.data
                director.birth_date = form.birth_date.data
                director.country = form.country.data
                db.session.commit()
                flash("Director information updated")
                return redirect(url_for("director_details", director_id=director.director_id))
    else:
        flash('This director does not exists')
        return redirect(url_for("list_objects"))
    return render_template('director_change.html', today=today, form=form, director=director)


@app.route('/add_review_movie/<reviewer_type>/<reviewer_id>/<object_id>', methods=['GET', 'POST'])
@login_required
def add_review_movie(reviewer_type, reviewer_id, object_id):
    movie = db.session.query(Movie).filter(Movie.movie_id == object_id).first()
    if movie is None:
        flash("This movie does not exists")
        return redirect(url_for("list_objects"))
    else:
        review = Review(author_type=reviewer_type,
                        review_object='f',
                        movie_id=movie.movie_id,
                        posting_date=today)

        if reviewer_type == 'w':
            review.viewer_id = reviewer_id
        elif reviewer_type == 'd':
            review.journalist_id = reviewer_id
        else:
            flash('Review can be added only by viewer and journalist')
            return redirect(url_for("list_objects"))

        review_db = db.session.query(Review).filter(Review.author_type == review.author_type,
                                                    Review.viewer_id == review.viewer_id,
                                                    Review.journalist_id == review.journalist_id,
                                                    Review.movie_id == review.movie_id,
                                                    Review.series_id == review.series_id,
                                                    Review.actor_id == review.actor_id).first()
        if review_db:
            flash('This user has already posted review to this movie')
            return redirect(url_for("edit_review", object_type='f', object_id=movie.movie_id))
        else:
            form = AddReviewMovie()
            if form.validate_on_submit():
                review.rate = form.rate.data
                review.content = form.content.data

                db.session.add(review)
                db.session.commit()
                # count mean of reviews
                command = text("SELECT filmweb.mean_rate(:pMovieId);")
                command = command.bindparams(pMovieId=movie.movie_id)
                res_text = ""
                for res in db.session.execute(command):
                    res_text = str(res).split('Decimal')[1].split(',')[0][2:-2]
                movie.viewers_rating = float(res_text)
                db.session.commit()
                flash("Movie review successfully added")
                return redirect(url_for("movie_details", movie_id=movie.movie_id))

    return render_template('add_review_movie.html', today=today, form=form, movie=movie)


@app.route('/edit_review/<object_type>/<object_id>', methods=['GET', 'POST'])
@login_required
def edit_review(object_type, object_id):
    review = Review(author_type=current_user.user_type,
                    review_object=object_type)
    movie = None
    series = None
    actor = None

    if object_type == 'f':
        movie = db.session.query(Movie).filter(Movie.movie_id == object_id).first()
        review.movie_id = object_id
    elif object_type == 's':
        series = db.session.query(Series).filter(Series.series_id == object_id).first()
        review.series_id = object_id
    elif object_type == 'a':
        actor = db.session.query(Actor).filter(Actor.actor_id == object_id).first()
        review.actor_id = object_id
    else:
        flash("No such object type")
        return redirect(url_for("list_objects"))

    if movie is None and series is None and actor is None:
        flash("This object does not exists")
        return redirect(url_for("list_objects"))
    else:
        if current_user.user_type == 'w':
            review.viewer_id = current_user.user_id
        elif current_user.user_type == 'd':
            review.journalist_id = current_user.user_id
        else:
            flash('Review can be added only by viewer and journalist')
            return redirect(url_for("list_objects"))

        review_db = db.session.query(Review).filter(Review.author_type == review.author_type,
                                                    Review.viewer_id == review.viewer_id,
                                                    Review.journalist_id == review.journalist_id,
                                                    Review.movie_id == review.movie_id,
                                                    Review.series_id == review.series_id,
                                                    Review.actor_id == review.actor_id).first()
        if review_db is None:
            flash('This user has not posted review to this object')
            return redirect(url_for("list_objects"))
        else:
            form = EditReview(rate=review_db.rate, content=review_db.content)
            if form.validate_on_submit():
                review_db.rate = form.rate.data
                review_db.content = form.content.data
                review_db.posting_date = today
                db.session.commit()

                # calculate average rate
                all_reviews = db.session.query(Review).filter(Review.movie_id == review.movie_id,
                                                              Review.series_id == review.series_id,
                                                              Review.actor_id == review.actor_id)
                reviews_sum = 0
                reviews_num = 0
                for rev in all_reviews:
                    reviews_sum += rev.rate
                    reviews_num += 1
                avg_rev = float(reviews_sum/reviews_num)
                if object_type == 'f':
                    movie.viewers_rating = avg_rev
                elif object_type == 's':
                    series.viewers_rating = avg_rev
                elif object_type == 'a':
                    actor.viewers_rating = avg_rev
                db.session.commit()

                flash("Review successfully edited")
                return redirect(url_for("list_objects"))

    return render_template('edit_review.html', today=today, form=form)

@app.route('/delete_studio/', methods=['GET', 'POST'])
@login_required
def delete_studio():
    studio = db.session.query(Studio).filter(Studio.studio_id == current_user.user_id).first()
    user = db.session.query(Users).filter(Users.user_id == studio.studio_id).first()
    movies = db.session.query(Movie).filter(Movie.studio_id == studio.studio_id).first()
    series = db.session.query(Series).filter(Series.studio_id == studio.studio_id).first()
    actors = db.session.query(Actor).filter(Actor.studio_id == studio.studio_id).first()
    directors = db.session.query(Director).filter(Director.studio_id == studio.studio_id).first()
    if not (movies or series or actors or directors):
        db.session.delete(studio)
        db.session.delete(user)
        db.session.commit()
        flash('Studio successfully deleted')
        return redirect(url_for('home'))
    else:
        flash('Cannot delete studio that is assigned to movie, series, actor or director.')
        return redirect(url_for('studio_details', studio_id=studio.studio_id))

@app.route('/delete_director/<director_id>', methods=['GET', 'POST'])
@login_required
def delete_director(director_id):
    director = db.session.query(Director).filter(Director.director_id == director_id).first()
    movies = db.session.query(Movie).filter(Movie.director_id == director_id).first()
    series = db.session.query(Series).filter(Series.director_id == director_id).first()
    if not (movies or series):
        db.session.delete(director)
        db.session.commit()
        flash('Director successfully deleted')
        return redirect(url_for('home'))
    else:
        flash('Cannot delete director that is assigned to movie or series.')
        return redirect(url_for('director_details', director_id=director_id))

@app.route('/delete_actor/<actor_id>', methods=['GET', 'POST'])
@login_required
def delete_actor(actor_id):
    actor = db.session.query(Actor).filter(Actor.actor_id == actor_id).first()
    movie_characters = db.session.query(Movie_character).filter(Movie_character.actor_id == actor_id).first()
    series_characters = db.session.query(Series_character).filter(Series_character.actor_id == actor_id).first()
    if not (movie_characters or series_characters):
        db.session.delete(actor)
        db.session.commit()
        flash('Actor successfully deleted')
        return redirect(url_for('home'))
    else:
        flash('Cannot delete actor that is assigned to movie characters or series characters.')
        return redirect(url_for('actor_details', actor_id=actor_id))

@app.route('/delete_movie/<movie_id>')
@login_required
def delete_movie(movie_id):
    flash('Cannot delete movie that is assigned to studio')
    return redirect(url_for('movie_details', movie_id=movie_id))

@app.route('/delete_series/<series_id>')
@login_required
def delete_series(series_id):
    flash('Cannot delete series that is assigned to studio')
    return redirect(url_for('series_details', series_id=series_id))

@app.route('/delete_review/<object_type>/<object_id>', methods=['GET', 'POST'])
@login_required
def delete_review(object_type, object_id):
    review = Review(author_type=current_user.user_type,
                    review_object=object_type)
    movie = None
    series = None
    actor = None

    if object_type == 'f':
        movie = db.session.query(Movie).filter(Movie.movie_id == object_id).first()
        review.movie_id = object_id
    elif object_type == 's':
        series = db.session.query(Series).filter(Series.series_id == object_id).first()
        review.series_id = object_id
    elif object_type == 'a':
        actor = db.session.query(Actor).filter(Actor.actor_id == object_id).first()
        review.actor_id = object_id
    else:
        flash("No such object type")
        return redirect(url_for("list_objects"))

    if movie is None and series is None and actor is None:
        flash("This object does not exists")
        return redirect(url_for("list_objects"))
    else:
        if current_user.user_type == 'w':
            review.viewer_id = current_user.user_id
        elif current_user.user_type == 'd':
            review.journalist_id = current_user.user_id
        else:
            flash('Review can be added only by viewer and journalist')
            return redirect(url_for("list_objects"))

        print(review.author_type, review.viewer_id, review.review_object, review.movie_id)
        review_db = db.session.query(Review).filter(Review.author_type == review.author_type,
                                                    Review.viewer_id == review.viewer_id,
                                                    Review.journalist_id == review.journalist_id,
                                                    Review.movie_id == review.movie_id,
                                                    Review.series_id == review.series_id,
                                                    Review.actor_id == review.actor_id).first()
        if review_db is None:
            flash('This user has not posted review to this object')
            return redirect(url_for("list_objects"))
        else:
            db.session.delete(review_db)
            db.session.commit()

            # calculate average rate
            all_reviews = db.session.query(Review).filter(Review.movie_id == review.movie_id,
                                                          Review.series_id == review.series_id,
                                                          Review.actor_id == review.actor_id)
            reviews_sum = 0
            reviews_num = 0
            for rev in all_reviews:
                reviews_sum += rev.rate
                reviews_num += 1
            avg_rev = float(reviews_sum / reviews_num)
            if object_type == 'f':
                movie.viewers_rating = avg_rev
            elif object_type == 's':
                series.viewers_rating = avg_rev
            elif object_type == 'a':
                actor.viewers_rating = avg_rev
            db.session.commit()

            flash("Review successfully deleted")
            return redirect(url_for("list_objects"))

@app.route('/news', methods=['GET','POST'])
@login_required
def news():
    news = db.session.query(News)
    studios = db.session.query(Studio)
    journalists = db.session.query(Journalist)
    return render_template('news.html', today=today, news=news, studios=studios, journalists=journalists)

@app.route('/news/<news_id>')
@login_required
def single_news(news_id):
    news = db.session.query(News).filter(News.news_id == news_id).first()
    studio = db.session.query(Studio).filter(Studio.studio_id == news.studio_id).first()
    journalist = db.session.query(Journalist).filter(Journalist.journalist_id == news.journalist_id).first()
    return render_template('single_news.html', today=today, news=news, studio=studio, journalist=journalist)

@app.route('/add_news', methods=['GET','POST'])
@login_required
def add_news():
    if current_user.user_type not in ['s', 'a', 'd']:
        flash("Only studio or journalist can add news")
        return redirect(url_for("news"))
    form = AddNews()
    if form.validate_on_submit():
        news = db.session.query(News).filter(
            News.title == form.title.data,
            News.content == form.content.data,
            News.publication_date == today
        ).first()
        if news is None:
            if current_user.user_type == 's':
                studio_id = current_user.user_id
                journalist_id = None
            else:
                studio_id = None
                journalist_id = current_user.user_id
        
            news = News(
                title=form.title.data,
                content=form.content.data,
                publication_date=today,
                journalist_id=journalist_id,
                studio_id=studio_id
            )
            db.session.add(news)
            db.session.commit()

            flash("News added successfully")
            return redirect(url_for("news"))
        else:
            flash("This news has already been added to the database")
    return render_template('add_news.html', today=today, form=form)

@app.route('/delete_news/<news_id>', methods=['GET','POST'])
@login_required
def delete_news(news_id):
    news = db.session.query(News).filter(News.news_id == news_id).first()
    db.session.delete(news)
    db.session.commit()
    flash("News deleted successfylly")
    return redirect(url_for('news'))


@app.route('/edit_news/<news_id>', methods=['GET','POST'])
@login_required
def edit_news(news_id):
    news = db.session.query(News).filter(News.news_id == news_id).first()
    form = EditNews(title=news.title, content=news.content)
    #form.title.data = news.title
    #form.content.data = news.content
    if form.validate_on_submit():
        check_news = db.session.query(News).filter(
            News.title == form.title.data,
            News.content == form.content.data,
            News.publication_date == news.publication_date
        ).first()
        if check_news is None:
            news.title = form.title.data
            news.content = form.content.data
            db.session.commit()
            flash("News edited successfully")
            return redirect(url_for("news"))
        elif check_news.news_id == news.get_id():
            flash("You didn't change anything")
        else:
            flash("This news has already been added to the database")

    return render_template('edit_news.html', today=today, form=form)

@app.route('/journalist_details/<journalist_id>')
def journalist_details(journalist_id=None):
    journalist = db.session.query(Journalist).filter(Journalist.journalist_id == journalist_id).first()
    if journalist:
        reviews = db.session.query(Review).filter(Review.author_type == 'd', Review.journalist_id == journalist_id)
        user = db.session.query(Users).filter(Users.user_id == journalist_id).first()
        movies = []
        series = []
        actors = []
        for review in reviews:
            if review.review_object == 'f':
                movies.append(db.session.query(Movie).filter(Movie.movie_id == review.movie_id).first())
            elif review.review_object == 's':
                series.append(db.session.query(Series).filter(Series.series_id == review.series_id).first())
            elif review.review_object == 'a':
                actors.append(db.session.query(Actor).filter(Actor.actor_id == review.actor_id).first()) 
    else:
        flash('This journalist does not exists')
        return redirect(url_for('home'))
    return render_template('journalist_details.html', today=today, journalist=journalist, reviews=reviews, 
                        movies=movies, series=series, actors=actors, user=user)

@app.route('/series_details/<series_id>')
def series_details(series_id=None):
    series = db.session.query(Series).filter(Series.series_id == series_id).first()
    if series:
        studio = db.session.query(Studio).filter(Studio.studio_id == series.studio_id).first()
        director = db.session.query(Director).filter(Director.director_id == series.director_id).first()
        genres = db.session.query(Series_genres).filter(Series_genres.series_id == series_id)
        genres_str =''
        for genre in genres:
            genres_str += ', ' + genre.genre
        genres_str = genres_str[2:]
        v_reviews = db.session.query(Review).filter(Review.series_id == series_id, Review.author_type == 'w')
        j_reviews = db.session.query(Review).filter(Review.series_id == series_id, Review.author_type == 'd')
        viewers = db.session.query(Viewer)
        journalists = db.session.query(Journalist)
        characters = db.session.query(Series_character).filter(Series_character.series_id == series_id)
        actors=[]
        for character in characters:
            actors.append(db.session.query(Actor).filter(Actor.actor_id == character.actor_id).first())
        actors = list(set(actors))
    else:
        flash("This series does not exists")
        return redirect(url_for("list_objects"))
    return render_template('series_details.html', today=today, series=series, studio=studio, director=director, genres=genres_str,
                        v_reviews=v_reviews, j_reviews=j_reviews, viewers=viewers, journalists=journalists, characters=characters, actors=actors)

@app.route('/like/<review_id>/<action>')
@login_required
def like_action(review_id, action):
    review = db.session.query(Review).filter(Review.review_id == review_id).first_or_404()
    if action == 'like':
        review.like_post(current_user)
        db.session.commit()
        all_reviews = db.session.query(ReviewRating).filter(ReviewRating.review_id == review.review_id)
        reviews_sum = 0
        reviews_num = 0
        for rev in all_reviews:
            reviews_sum += rev.viewers_rating
            reviews_num += 1
        review.viewers_rating = float(reviews_sum / reviews_num)*2+3
        db.session.commit()
    elif action == 'dislike':
        review.dislike_post(current_user)
        db.session.commit()
        all_reviews = db.session.query(ReviewRating).filter(ReviewRating.review_id == review.review_id)
        reviews_sum = 0
        reviews_num = 0
        for rev in all_reviews:
            reviews_sum += rev.viewers_rating
            reviews_num += 1
        review.viewers_rating = float(reviews_sum / reviews_num)*2+3
        db.session.commit()
    elif action == 'unlike':
        review.unlike_post(current_user)
        db.session.commit()
        all_reviews = db.session.query(ReviewRating).filter(ReviewRating.review_id == review.review_id)
        reviews_sum = 0
        reviews_num = 0
        for rev in all_reviews:
            reviews_sum += rev.viewers_rating
            reviews_num += 1
        review.viewers_rating = float(reviews_sum / reviews_num)*2+3
        db.session.commit()
    return redirect(request.referrer)

@app.route('/actor_details/<actor_id>')
def actor_details(actor_id=None):
    actor = db.session.query(Actor).filter(Actor.actor_id == actor_id).first()
    if actor:
        studio = db.session.query(Studio).filter(Studio.studio_id == actor.studio_id).first()
        movie_characters = db.session.query(Movie_character).filter(Movie_character.actor_id == actor_id)
        series_characters = db.session.query(Series_character).filter(Series_character.actor_id == actor_id)
        movies = []
        for character in movie_characters:
            movies.append(db.session.query(Movie).filter(Movie.movie_id == character.movie_id).first())
        series = []
        for character in series_characters:
            series.append(db.session.query(Series).filter(Series.series_id == character.series_id).first())
        v_reviews = db.session.query(Review).filter(Review.actor_id == actor_id, Review.author_type == 'w')
        j_reviews = db.session.query(Review).filter(Review.actor_id == actor_id, Review.author_type == 'd')
        viewers = db.session.query(Viewer)
        journalists = db.session.query(Journalist)
    else:
        flash("This actor does not exists")
        return redirect(url_for("list_objects"))
    return render_template('actor_details.html', today=today, studio=studio, actor=actor, movies=movies, series=series,
        movie_characters=movie_characters, series_characters=series_characters, v_reviews=v_reviews, j_reviews=j_reviews,
        viewers=viewers, journalists=journalists)

@app.route('/add_review_series/<reviewer_type>/<reviewer_id>/<object_id>', methods=['GET', 'POST'])
@login_required
def add_review_series(reviewer_type, reviewer_id, object_id):
    series = db.session.query(Series).filter(Series.series_id == object_id).first()
    if series is None:
        flash("This series does not exists")
        return redirect(url_for("list_objects"))
    else:
        review = Review(author_type=reviewer_type,
                        review_object='s',
                        series_id=series.series_id,
                        posting_date=today)

        if reviewer_type == 'w':
            review.viewer_id = reviewer_id
        elif reviewer_type == 'd':
            review.journalist_id = reviewer_id
        else:
            flash('Review can be added only by viewer and journalist')
            return redirect(url_for("list_objects"))

        review_db = db.session.query(Review).filter(Review.author_type == review.author_type,
                                                    Review.viewer_id == review.viewer_id,
                                                    Review.journalist_id == review.journalist_id,
                                                    Review.movie_id == review.movie_id,
                                                    Review.series_id == review.series_id,
                                                    Review.actor_id == review.actor_id).first()
        if review_db:
            flash('This user has already posted review to this series')
            return redirect(url_for("edit_review", object_type='s', object_id=series.series_id))
        else:
            form = AddReviewSeries()
            if form.validate_on_submit():
                review.rate = form.rate.data
                review.content = form.content.data

                db.session.add(review)
                db.session.commit()

                # calculate average rate
                all_reviews = db.session.query(Review).filter(Review.series_id == review.series_id)
                reviews_sum = 0
                reviews_num = 0
                for rev in all_reviews:
                    reviews_sum += rev.rate
                    reviews_num += 1
                series.viewers_rating = float(reviews_sum/reviews_num)
                db.session.commit()

                flash("Series review successfully added")
                return redirect(url_for("series_details", series_id=series.series_id))

    return render_template('add_review_series.html', today=today, form=form, series=series)

@app.route('/add_review_actor/<reviewer_type>/<reviewer_id>/<object_id>', methods=['GET', 'POST'])
@login_required
def add_review_actor(reviewer_type, reviewer_id, object_id):
    actor = db.session.query(Actor).filter(Actor.actor_id == object_id).first()
    if actor is None:
        flash("This actor does not exists")
        return redirect(url_for("list_objects"))
    else:
        review = Review(author_type=reviewer_type,
                        review_object='a',
                        actor_id=actor.actor_id,
                        posting_date=today)

        if reviewer_type == 'w':
            review.viewer_id = reviewer_id
        elif reviewer_type == 'd':
            review.journalist_id = reviewer_id
        else:
            flash('Review can be added only by viewer and journalist')
            return redirect(url_for("list_objects"))

        review_db = db.session.query(Review).filter(Review.author_type == review.author_type,
                                                    Review.viewer_id == review.viewer_id,
                                                    Review.journalist_id == review.journalist_id,
                                                    Review.movie_id == review.movie_id,
                                                    Review.series_id == review.series_id,
                                                    Review.actor_id == review.actor_id).first()
        if review_db:
            # TODO: redirect user to edit review page
            flash('This user has already posted review to this actor')
            return redirect(url_for("edit_review", object_type='a', object_id=actor.actor_id))
        else:
            form = AddReviewActor()
            if form.validate_on_submit():
                review.rate = form.rate.data
                review.content = form.content.data

                db.session.add(review)
                db.session.commit()

                # calculate average rate
                all_reviews = db.session.query(Review).filter(Review.actor_id == review.actor_id)
                reviews_sum = 0
                reviews_num = 0
                for rev in all_reviews:
                    reviews_sum += rev.rate
                    reviews_num += 1
                actor.viewers_rating = float(reviews_sum/reviews_num)
                db.session.commit()

                flash("Actor review successfully added")
                return redirect(url_for("actor_details", actor_id=actor.actor_id))

    return render_template('add_review_actor.html', today=today, form=form, actor=actor)

@app.route('/viewer_details/<viewer_id>')
@login_required
def viewer_details(viewer_id=None):
    viewer = db.session.query(Viewer).filter(Viewer.viewer_id == viewer_id).first()
    if viewer.is_public == 'f':
        flash("Change account type to public in order to get access")
        return redirect(url_for('viewer_change'))
    if viewer:
        reviews = db.session.query(Review).filter(Review.author_type == 'w', Review.viewer_id == viewer_id)
        user = db.session.query(Users).filter(Users.user_id == viewer_id).first()
        movies = []
        series = []
        actors = []
        for review in reviews:
            if review.review_object == 'f':
                movies.append(db.session.query(Movie).filter(Movie.movie_id == review.movie_id).first())
            elif review.review_object == 's':
                series.append(db.session.query(Series).filter(Series.series_id == review.series_id).first())
            elif review.review_object == 'a':
                actors.append(db.session.query(Actor).filter(Actor.actor_id == review.actor_id).first()) 
    else:
        flash('This viewer does not exists')
        return redirect(url_for("list_objects"))
    return render_template('viewer_details.html', today=today, movies=movies, series=series, actors=actors, reviews=reviews, viewer=viewer, user=user)



if __name__ == '__main__':
    # Flask-SQLAlchemy 3.0 all access to db.engine (and db.session) requires an active Flask application context
    with app.app_context():
        initGenres()
        # db.drop_all()
        # db.create_all()
    app.run(debug=True)
