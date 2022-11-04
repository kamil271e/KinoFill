from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus

app = Flask(__name__)
app.secret_key = '123'
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://postgres:{quote_plus('Welcome1@')}@localhost/WebGameOn"
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost/WebGameOn'
# app.config['UPLOAD_FOLDER'] = "static/images/"
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'quote': False, 'schema': 'public'}

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), unique=True, nullable=False)

    def __init__(self, login):
        self.login = login

    def __repr__(self):
        return f"<User {self.login}>"

# db.create_all()
@app.route('/')
def home():
    user = User(login='cos')
    db.session.add(user)
    db.session.commit()

if __name__ == '__main__':
    # db.create_all()
    app.run(debug=True)
