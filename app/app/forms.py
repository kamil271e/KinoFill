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


class AddFilm(FlaskForm):
    title = StringField("Tytuł", validators=[DataRequired()])
    production_date = DateField("Data produkcji", validators=[DataRequired()])
    runtime = StringField("Długość (w minutach)")
    # director = SelectField("Reżyserowie", )
    submit = SubmitField("Dodaj film")


class AddDirector(FlaskForm):
    firstname = StringField("Imię", validators=[DataRequired()])
    surname = StringField("Nazwisko", validators=[DataRequired()])
    birth_date = DateField("Data urodzenia")#, format='%d.%m.%Y', validators=[DataRequired()])
    country = SelectField("Kraj pochodzenia", choices=countries)
    submit = SubmitField("Dodaj reżysera")

    def validate(self):
        if self.birth_date.data >= datetime.datetime.strptime(today, "%d.%m.%Y").date():
            flash("Data musi być przeszła")
            return False
        if len(self.firstname.data.strip()) < 3:
            flash("Wprowadź poprawne imię")
            return False
        if len(self.surname.data.strip()) < 3:
            flash("Wprowadź poprawne nazwisko")
            return False
        if self.country.data == '-':
            self.country.data = None
        return True

