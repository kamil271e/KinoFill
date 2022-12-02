from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus
from flask_fontawesome import FontAwesome
from flask_login import login_user, login_required, logout_user, current_user
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField, EmailField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Length

app = Flask(__name__)
fa = FontAwesome(app)
app.secret_key = '123'
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://postgres:{quote_plus('Welcome1@')}@localhost/Filmweb2"
# app.config['UPLOAD_FOLDER'] = "static/images/"
db = SQLAlchemy(app)

global today
today = date.today().strftime("%d.%m.%Y")

