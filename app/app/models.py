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
