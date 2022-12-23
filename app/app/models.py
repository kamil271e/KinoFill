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