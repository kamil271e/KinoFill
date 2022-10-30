from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus

def print_hi(name):
    print(f'Hi, {name}')

if __name__ == '__main__':
    print_hi('PyCharm')

app = Flask(__name__)
# app.secret_key = '123'
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://postgres:{quote_plus('Welcome1@')}@localhost/Filmweb2"
# app.config['UPLOAD_FOLDER'] = "static/images/"
# db = SQLAlchemy(app)

