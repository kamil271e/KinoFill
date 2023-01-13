from config import *

class RegisterForm(FlaskForm):
    login = StringField("Login", validators=[DataRequired(), Length(5, 16)])
    password = PasswordField("Hasło", validators=[DataRequired(), Length(5, 16)])
    role = SelectField("Rola", choices=["Widz", "Dziennikarz", "Wytwórnia filmowa"])
    user_desc = StringField("Opis profilu", widget=TextArea())
    viewer_role = SelectField("Typ konta", choices=["Prywatne", "Publiczne"])
    name = StringField("Nazwa")
    submit = SubmitField("Zarejestruj")

    def validate(self):
        if self.role.data != "Widz" or self.viewer_role.data == "Publiczne":
            name = self.name.data.strip()
            if len(name) < 1:
                # self.name.errors.append('Prosze podac nazwe użytkownika')
                flash('Prosze podac nazwe użytkownika')
                return False
            elif len(name) > 20 or len(name) < 5:
                # self.name.errors.append("Nazwa uzytkownika powinna mieć od 5 do 20 znaków")
                flash("Nazwa uzytkownika powinna mieć od 5 do 20 znaków")
                return False
        return True


class AddMovie(FlaskForm):
    name = StringField("Tytuł", validators=[DataRequired()])
    creation_year = SelectField('Rok produkcji', coerce=int, choices=range(int(today[6:]), int(today[6:]) - 100, -1))
    length = StringField("Długość (w minutach)", validators=[DataRequired()])
    director = SelectField("Reżyser")
    studio = SelectField("Wytwórnia")
    # choices = [('value1', 'label1'), ('value2', 'label2'), ('value3', 'label3')]
    # genre = SelectMultipleField("Gatunek", choices=choices) # TODO multiple choices
    genre = SelectField("Gatunek")
    submit = SubmitField("Dodaj film")

    def validate(self):
        try:
            _ = int(self.length.data)
        except:
            flash("Długość filmu musi być liczbą całkowitą")
            return False

        if int(self.length.data) <= 0:
            flash("Podaj poprawną długość trwania filmu")
            return False
        if len(self.name.data.strip()) > 30:
            flash("Podano za długą nazwę")
            return False
        return True


class AddDirector(FlaskForm):
    firstname = StringField("Imię", validators=[DataRequired()])
    surname = StringField("Nazwisko", validators=[DataRequired()])
    birth_date = DateField("Data urodzenia", validators=[DataRequired()])#, format='%d.%m.%Y', validators=[DataRequired()])
    country = SelectField("Kraj pochodzenia", choices=countries)
    submit = SubmitField("Dodaj reżysera")

    def validate(self):
        if self.birth_date.data >= datetime.datetime.strptime(today, "%d.%m.%Y").date():
            flash("Data musi być przeszła")
            return False
        if len(self.firstname.data.strip()) < 3 or len(self.firstname.data.strip()) > 20:
            flash("Wprowadź poprawne imię")
            return False
        if len(self.surname.data.strip()) < 3 or len(self.surname.data.strip()) > 20:
            flash("Wprowadź poprawne nazwisko")
            return False
        if self.country.data == '-':
            self.country.data = None
        return True


class AddSeries(FlaskForm):
    name = StringField("Tytuł", validators=[DataRequired()])                          
    episodes = StringField("Liczba odcinków", default=10, validators=[NumberRange(min=0, max=10000)], render_kw={'step': 1})
    seasons = DecimalRangeField("Liczba sezonów", default=1, validators=[NumberRange(min=0, max=200)], render_kw={'step': 1})
    director = SelectField("Reżyser")
    studio = SelectField("Wytwórnia")
    genre = SelectField("Gatunek")
    submit = SubmitField("Dodaj serial")

    def validate(self):
        try:
            self.episodes.data = int(self.episodes.data)
        except:
            flash("Liczba odcinków musi być liczbą całkowitą")
            return False

        if len(self.name.data.strip()) > 30:
            flash("Podano za długą nazwę")
            return False
        if int(self.episodes.data) < 0:
            flash("Liczba odcinków nie może być ujemna")
            return False

        self.seasons.data = int(self.seasons.data)
        
        return True
