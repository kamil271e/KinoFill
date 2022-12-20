from config import *


class Users(db.Model, UserMixin):
    __tablename__ = "uzytkownicy"
    __table_args__ = {'quote': False, 'schema': "filmweb"}

    id_uzytkownika = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(20), unique=True, nullable=False)
    haslo = db.Column(db.String(128))
    data_dolaczenia = db.Column(db.Date)
    opis_profilu = db.Column(db.String(256))
    aktywny = db.Column(db.String(1))
    typ_uzytkownika = db.Column(db.String(1))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.haslo = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.haslo, password)

    def __init__(self, login, password, today, user_type, desc=None, active='t'):
        self.login = login
        self.haslo = password
        self.data_dolaczenia = today
        self.opis_profilu = desc
        self.aktywny = active
        self.typ_uzytkownika = user_type


class Viewer(db.Model):
    __tablename__ = "viewers"
    __table_args__ = {'quote': False, 'schema': "filmweb", }

    viewer_id = db.Column(db.Integer, db.ForeignKey("filmweb.users.id"), primary_key=True)
    is_public = db.Column(db.String(1), nullable=False) # y - public, n - private
    name = db.Column(db.String(20))

    def __init__(self, viewer_id, is_public, name):
        self.viewer_id = viewer_id
        self.is_public = is_public
        self.name = name


class Journalist(db.Model):
    __tablename__ = "journalists"
    __table_args__ = {'quote': False, 'schema': "filmweb", }

    journalist_id = db.Column(db.Integer, db.ForeignKey("filmweb.users.id"), primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    firstname = db.Column(db.String(20))
    surname = db.Column(db.String(20))
    birthday = db.Column(db.Date)

    def __init__(self, journalist_id, name, firstname='', surname='', birthday=''):
        self.journalist_id = journalist_id
        self.name = name
        self.firstname = firstname
        self.surname = surname
        self.birthday = birthday


class Studio(db.Model):
    __tablename__ = "studios"
    __table_args__ = {'quote': False, 'schema': "filmweb", }

    studio_id = db.Column(db.Integer, db.ForeignKey("filmweb.users.id"), primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    country = db.Column(db.String(20))
    creation_date = db.Column(db.Date)
    viewers_grade = db.Column(db.Float)

    def __init__(self, studio_id, name, country='', creation_date=today, viewers_grade=0.0):
        self.studio_id = studio_id
        self.name = name
        self.country = country
        self.creation_date = creation_date
        self.viewers_grade = viewers_grade