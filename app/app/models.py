from config import *
# from forms import *

class User(db.Model):
    __tablename__ = "users"
    __table_args__ = {'quote': False, 'schema': "filmweb"}

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    register_date = db.Column(db.Date)
    role = db.Column(db.String(5))
    user_desc = db.Column(db.String(256))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __init__(self, login, password_hash, today, role, desc=None):
        self.login = login
        self.password_hash = password_hash
        self.role = role
        self.register_date = today
        self.user_desc = desc


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
