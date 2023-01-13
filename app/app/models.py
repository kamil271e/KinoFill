from config import *


class Users(db.Model, UserMixin):
    __tablename__ = "users"
    __table_args__ = {'quote': False, 'schema': "filmweb"}

    user_id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    join_date = db.Column(db.Date)
    description = db.Column(db.String(256))
    active = db.Column(db.String(1))
    user_type = db.Column(db.String(5))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __init__(self, login, password_hash, today, user_type, active, desc):
        self.login = login
        self.password_hash = password_hash
        self.join_date = today
        self.description = desc
        self.active = active
        self.user_type = user_type

    def get_id(self):
        return (self.user_id)


class Viewer(db.Model):
    __tablename__ = "viewers"
    __table_args__ = {'quote': False, 'schema': "filmweb", }

    viewer_id = db.Column(db.Integer, db.ForeignKey("filmweb.users.user_id"), primary_key=True)
    is_public = db.Column(db.String(1), nullable=False) # t - public, f - private
    nickname = db.Column(db.String(30))

    def __init__(self, viewer_id, is_public, name):
        self.viewer_id = viewer_id
        self.is_public = is_public
        self.nickname = name

    def get_id(self):
        return (self.viewer_id)


class Journalist(db.Model):
    __tablename__ = "journalists"
    __table_args__ = {'quote': False, 'schema': "filmweb", }

    journalist_id = db.Column(db.Integer, db.ForeignKey("filmweb.users.user_id"), primary_key=True)
    nickname = db.Column(db.String(20), nullable=False, unique=True)
    firstname = db.Column(db.String(20))
    surname = db.Column(db.String(20))
    birth_date = db.Column(db.Date)

    def __init__(self, journalist_id, nickname, firstname='', surname='', birth_date=''):
        self.journalist_id = journalist_id
        self.nickname = nickname
        self.firstname = firstname
        self.surname = surname
        self.birth_date = birth_date

    def get_id(self):
        return (self.journalist_id)


class Studio(db.Model):
    __tablename__ = "studios"
    __table_args__ = {'quote': False, 'schema': "filmweb", }

    studio_id = db.Column(db.Integer, db.ForeignKey("filmweb.users.user_id"), primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    country = db.Column(db.String(20))
    creation_date = db.Column(db.Date)
    viewers_rating = db.Column(db.Float)

    def __init__(self, studio_id, name, country='', creation_date=today, viewers_rating=0.0):
        self.studio_id = studio_id
        self.name = name
        self.country = country
        self.creation_date = creation_date
        self.viewers_rating = viewers_rating

    def get_id(self):
        return (self.studio_id)


class Director(db.Model):
    __tablename__ = "directors"
    __table_args__ = {'quote': False, 'schema': "filmweb", }

    director_id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(20), nullable=False, unique=True)
    surname = db.Column(db.String(20), nullable=False, unique=True)
    birth_date = db.Column(db.Date, nullable=False, unique=True)
    country = db.Column(db.String(20))
    rate = db.Column(db.Float)
    studio_id = db.Column(db.Integer, db.ForeignKey("filmweb.studios.studio_id"))

    def __init__(self, firstname, surname, birth_date, country, rate, studio_id):
        self.firstname = firstname
        self.surname = surname
        self.birth_date = birth_date
        self.country = country
        self.rate = rate
        self.studio_id = studio_id

    def get_id(self):
        return (self.director_id)


class Movie(db.Model):
    __tablename__ = "movies"
    __table_args__ = {'quote': False, 'schema': "filmweb", }

    movie_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    creation_year = db.Column(db.Integer, nullable=False, unique=True)
    length = db.Column(db.Integer, nullable=False)
    viewers_rating = db.Column(db.Float)
    studio_id = db.Column(db.Integer, db.ForeignKey("filmweb.studios.studio_id"), nullable=False)
    director_id = db.Column(db.Integer, db.ForeignKey("filmweb.directors.director_id"), nullable=False)

    def __init__(self, name, creation_year, length, viewers_rating, studio_id, director_id):
        self.name = name
        self.creation_year = creation_year
        self.length = length
        self.viewers_rating = viewers_rating
        self.studio_id = studio_id
        self.director_id = director_id

    def get_id(self):
        return (self.movie_id)

class Series(db.Model):
    __tablename__ = "series"
    __table_args__ = {'quote': False, 'schema': "filmweb", }

    series_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    episodes = db.Column(db.Integer, nullable=False, unique=True)
    seasons = db.Column(db.Integer, nullable=False)
    viewers_rating = db.Column(db.Float)
    studio_id = db.Column(db.Integer, db.ForeignKey("filmweb.studios.studio_id"), nullable=False)
    director_id = db.Column(db.Integer, db.ForeignKey("filmweb.directors.director_id"), nullable=False)

    def __init__(self, name, episodes, seasons, viewers_rating, studio_id, director_id):
        self.name = name
        self.episodes = episodes
        self.seasons = seasons
        self.viewers_rating = viewers_rating
        self.studio_id = studio_id
        self.director_id = director_id

    def get_id(self):
        return (self.series_id)


class Genres(db.Model):
    __tablename___ = "genres"
    __table_args__ = {'quote': False, 'schema': "filmweb", }

    genre = db.Column(db.String(20), primary_key=True)

    def __init__(self, genre):
        self.genre = genre
    
class Movie_genres(db.Model):
    __tablename___ = "movie_genres"
    __table_args__ = {'quote': False, 'schema': "filmweb", }

    movie_id = db.Column(db.Integer, db.ForeignKey("filmweb.movies.movie_id"), primary_key = True)
    genre = db.Column(db.String(20), db.ForeignKey("filmweb.genres.genre"), primary_key=True)

    def __init__(self, movie_id, genre):
        self.movie_id = movie_id
        self.genre = genre

class Series_genres(db.Model):
    __tablename___ = "series_genres"
    __table_args__ = {'quote': False, 'schema': "filmweb", }

    series_id = db.Column(db.Integer, db.ForeignKey("filmweb.series.series_id"), primary_key = True)
    genre = db.Column(db.String(20), db.ForeignKey("filmweb.genres.genre"), primary_key=True)

    def __init__(self, series_id, genre):
        self.series_id = series_id
        self.genre = genre

