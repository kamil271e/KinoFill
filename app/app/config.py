from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus
from flask_fontawesome import FontAwesome
from flask_login import login_user, login_required, logout_user, current_user, UserMixin, LoginManager
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField, EmailField, DateField, SelectMultipleField, DecimalRangeField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Length, NumberRange
import datetime

app = Flask(__name__)
fa = FontAwesome(app)
app.secret_key = '123'
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://postgres:{quote_plus('Welcome1@')}@localhost/Filmweb2"
# app.config['UPLOAD_FOLDER'] = "static/images/"
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.refresh_view = 'login'
login_manager.login_message = "Tylko zalogowani użytkownicy mają dostęp do pełnej zawartości"

global today
today = date.today().strftime("%d.%m.%Y")

global countries
countries = ["-","Afganistan","Wyspy Alandzkie","Albania","Algieria","Samoa Amerykańskie","Andora","Angola","Anguilla","Antarktyda","Antigua i Barbuda","Argentyna","Armenia","Aruba","Australia","Austria","Azerbejdżan","Bahamy","Bahrajn","Bangladesz","Barbados","Białoruś","Belgia","Belize","Benin","Bermudy","Bhutan","Boliwia","Niderlandy Karaibskie","Bośnia i Hercegowina","Botswana","Wyspa Bouveta","Brazylia","Brytyjskie Terytorium Oceanu Indyjskiego","Brunei","Bułgaria","Burkina Faso","Burundi","Kambodża","Kamerun","Kanada","Republika Zielonego Przylądka","Kajmany","Republika Środkowoafrykańska","Czad","Chile","Chiny","Wyspa Bożego Narodzenia","Wyspy Kokosowe","Kolumbia","Komory","Kongo","Demokratyczna Republika Konga","Wyspy Cooka","Kostaryka","Côte d’Ivoire","Chorwacja","Kuba","Curaçao","Cypr","Czechy","Dania","Dżibuti","Dominika","Dominikana","Ekwador","Egipt","Salwador","Gwinea Równikowa","Erytrea","Estonia","Etiopia","Falklandy (Malwiny)","Wyspy Owcze","Fidżi","Finlandia","Francja","Gujana Francuska","Polinezja Francuska","Francuskie Terytoria Południowe i Antarktyczne","Gabon","Gambia","Gruzja","Niemcy","Ghana","Gibraltar","Grecja","Grenlandia","Grenada","Gwadelupa","Guam","Gwatemala","Guernsey","Gwinea","Gwinea Bissau","Gujana","Haiti","Wyspy Heard i McDonalda","Watykan","Honduras","Hongkong","Węgry","Islandia","Indie","Indonezja","Iran","Irak","Irlandia","Wyspa Man","Izrael","Włochy","Jamajka","Japonia","Jersey","Jordania","Kazachstan","Kenia","Kiribati","Korea Północna","Korea Południowa","Kosowo","Kuwejt","Kirgistan","Laos","Łotwa","Liban","Lesotho","Liberia","Libia","Liechtenstein","Litwa","Luksemburg","Makau","Macedonia Północna","Madagaskar","Malawi","Malezja","Malediwy","Mali","Malta","Wyspy Marshalla","Martynika","Mauretania","Mauritius","Majotta","Meksyk","Mikronezja","Mołdawia","Monako","Mongolia","Czarnogóra","Montserrat","Maroko","Mozambik","Mjanma (Birma)","Namibia","Nauru","Nepal","Holandia","Curaçao","Nowa Kaledonia","Nowa Zelandia","Nikaragua","Niger","Nigeria","Niue","Norfolk","Mariany Północne","Norwegia","Oman","Pakistan","Palau","Palestyna","Panama","Papua-Nowa Gwinea","Paragwaj","Peru","Filipiny","Pitcairn","Polska","Portugalia","Portoryko","Katar","Reunion","Rumunia","Rosja","Rwanda","Saint-Barthélemy","Wyspa Świętej Heleny","Saint Kitts i Nevis","Saint Lucia","Saint-Martin","Saint-Pierre i Miquelon","Saint Vincent i Grenadyny","Samoa","San Marino","Wyspy Świętego Tomasza i Książęca","Arabia Saudyjska","Senegal","Serbia","Serbia","Seszele","Sierra Leone","Singapur","Sint Maarten","Słowacja","Słowenia","Wyspy Salomona","Somalia","Republika Południowej Afryki","Georgia Południowa i Sandwich Południowy","Sudan Południowy","Hiszpania","Sri Lanka","Sudan","Surinam","Svalbard i Jan Mayen","Eswatini","Szwecja","Szwajcaria","Syria","Tajwan","Tadżykistan","Tanzania","Tajlandia","Timor Wschodni","Togo","Tokelau","Tonga","Trynidad i Tobago","Tunezja","Turcja","Turkmenistan","Turks i Caicos","Tuvalu","Uganda","Ukraina","Zjednoczone Emiraty Arabskie","Wielka Brytania","Stany Zjednoczone","Dalekie Wyspy Mniejsze Stanów Zjednoczonych","Urugwaj","Uzbekistan","Vanuatu","Wenezuela","Wietnam","Brytyjskie Wyspy Dziewicze","Wyspy Dziewicze Stanów Zjednoczonych","Wallis i Futuna","Sahara Zachodnia","Jemen","Zambia","Zimbabwe"]
countries = sorted(countries)
