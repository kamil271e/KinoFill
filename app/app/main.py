from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus

app = Flask(__name__)
# app.secret_key = '123'
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://postgres:{quote_plus('Welcome1@')}@localhost/Filmweb2"
# app.config['UPLOAD_FOLDER'] = "static/images/"
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"
    __table_args__ = {'quote': False, 'schema': "filmweb"}

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), unique=True, nullable=False)

    def __init__(self, login):
        self.login = login

    # def __repr__(self):
    #     return f"<User {self.login}>"

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        print(request.form['login'])
        login = request.form['login']
        user = User(login)
        db.session.add(user)
        db.session.commit()
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context(): #Flask-SQLAlchemy 3.0 all access to db.engine (and db.session) requires an active Flask application context
        # db.drop_all()
        db.create_all()
    app.run(debug=True)
