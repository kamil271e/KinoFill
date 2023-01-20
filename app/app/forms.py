from config import *
from utils import *

class RegisterForm(FlaskForm):
    login = StringField("Login", validators=[DataRequired(), Length(5, 16)])
    password = PasswordField("Password", validators=[DataRequired(), Length(5, 16)])
    password_confirm = PasswordField("Confirm password", validators=[DataRequired(), Length(5,6)]) #, EqualTo('password', message="Passwords must match")])
    role = SelectField("Role", choices=["Viewer", "Journalist", "Studio"])
    user_desc = StringField("Profile description", widget=TextArea())
    viewer_role = SelectField("Account type", choices=["Private", "Public"])
    name = StringField("Name")
    submit = SubmitField("Register")

    def validate(self):
        if self.password.data != self.password_confirm.data:
            flash("Passwords must match")
            return False
        if self.role.data != "Viewer" or self.viewer_role.data == "Public":
            name = self.name.data.strip()
            if len(name) < 1:
                # self.name.errors.append('Please enter user name')
                flash('Please enter user name')
                return False
            elif len(name) > 20 or len(name) < 5:
                # self.name.errors.append("Nazwa uzytkownika powinna mieć od 5 do 20 znaków")
                flash("Username should have between 5 and 20 characters")
                return False
        return True


class AddMovie(FlaskForm):
    name = StringField("Title")
    creation_year = SelectField('Creation year', coerce=int, choices=range(int(today[6:]), int(today[6:]) - 100, -1))
    length = StringField("Length (in minutes)")
    director = SelectField("Director")
    studio = SelectField("Studio") # Only for admin to choose
    choose_studio = False
    submit = SubmitField("Add movie")
    redirect_add_director = SubmitField("Add director")

    def __init__(self, choose_studio, *args, **kwargs):
        self.choose_studio = choose_studio
        super(AddMovie, self).__init__(*args, **kwargs)

    def validate(self):
        if self.redirect_add_director.data:
            return True
        if not self.name.data:
            flash("Please enter username")
            return False
        if len(self.length.data) > 9:
            flash("Length of the movie cannot be that long")
            return False
        if not self.length.data:
            flash("Please enter length of the movie")
            return False
        try:
            _ = int(self.length.data)
        except:
            flash("Length of the movie needs to be an integer. Please try again")
            return False
        if int(self.length.data) <= 0:
            flash("Please enter valid length of the movie")
            return False
        if len(self.name.data.strip()) > 30:
            flash("The name must not exceeded 30 characters. Please try again")
            return False
        
        return True


class AddDirector(FlaskForm):
    firstname = StringField("Fisrt name", validators=[DataRequired()])
    surname = StringField("Surname", validators=[DataRequired()])
    birth_date = DateField("Birthdate", validators=[DataRequired()])#, format='%d.%m.%Y', validators=[DataRequired()])
    country = SelectField("Country", choices=countries)
    studio = SelectField("Studio") # Only for admin to choose
    choose_studio = False
    submit = SubmitField("Add director")

    def __init__(self, choose_studio, *args, **kwargs):
        self.choose_studio = choose_studio
        super(AddDirector, self).__init__(*args, **kwargs)

    def validate(self):
        if nameInvalid(self.firstname.data) or nameInvalid(self.surname.data):
            flash("First name and surname cannot have any numbers or special characters")
            return False
        if self.birth_date.data >= datetime.datetime.strptime(today, "%d.%m.%Y").date():
            flash("Date needs to be from past")
            return False
        if len(self.firstname.data.strip()) < 2 or len(self.firstname.data.strip()) > 20: # TODO numbers and sepcial characters handling
            flash("Enter valid name")
            return False
        if len(self.surname.data.strip()) < 2 or len(self.surname.data.strip()) > 20:
            flash("Enter valid surname")
            return False
        if self.country.data == '-':
            self.country.data = None
        self.firstname.data = convertName(self.firstname.data)
        self.surname.data = convertName(self.surname.data)
        return True


class AddSeries(FlaskForm):
    name = StringField("Title")                          
    episodes = StringField("Number of episodes")
    director = SelectField("Director")
    studio = SelectField("Studio")
    choose_studio = False
    genre = SelectField("Genre")
    submit = SubmitField("Add series")
    redirect_add_director = SubmitField("Add director")

    def __init__(self, choose_studio, *args, **kwargs):
        self.choose_studio = choose_studio
        super(AddSeries, self).__init__(*args, **kwargs)

    def validate(self):
        if self.redirect_add_director.data:
            return True
        if not self.name.data:
            flash("Please enter series title")
            return False
        if not self.episodes.data:
            flash("Please enter number of episodes")
            return False
        if len(self.episodes.data) > 9:
            flash("There can't be that many episodes")
            return False
        try:
            self.episodes.data = int(self.episodes.data)
        except:
            flash("Number of episodes needs to be an integer")
            return False
        if self.episodes.data < 0:
            flash("Number of episodes cannot be negative")
            return False
        if self.episodes.data < int(request.form['range']):
            flash("Number of seasons cannot be greater than number of episodes")
            return False
        if len(self.name.data.strip()) > 30:
            flash("Title is too long")
            return False
        if int(self.episodes.data) < 0:
            flash("Number of episodes cannot be negative")
            return False

        return True

class AddActor(FlaskForm):
    firstname = StringField("First name", validators=[DataRequired()])
    surname = StringField("Surname", validators=[DataRequired()])
    birth_date = DateField("Birthdate", validators=[DataRequired()])#, format='%d.%m.%Y', validators=[DataRequired()])
    country = SelectField("Country", choices=countries)
    studio = SelectField("Studio")
    choose_studio = False
    submit = SubmitField("Add actor")

    def __init__(self, choose_studio, *args, **kwargs):
        self.choose_studio = choose_studio
        super(AddActor, self).__init__(*args, **kwargs)

    def validate(self):
        if nameInvalid(self.firstname.data) or nameInvalid(self.surname.data):
            flash("First name and surname cannot have any numbers or special characters")
            return False
        if len(self.firstname.data.strip()) < 2 or len(self.firstname.data.strip()) > 20:
            flash("Enter valid firstname")
            return False
        if len(self.surname.data.strip()) < 2 or len(self.surname.data.strip()) > 20:
            flash("Enter valid surname")
            return False
        if self.birth_date.data >= datetime.datetime.strptime(today, "%d.%m.%Y").date():
            flash("Date needs to be from past")
            return False
        if self.country.data == '-':
            self.country.data = None
        self.firstname.data = convertName(self.firstname.data)
        self.surname.data = convertName(self.surname.data)
        return True

class ChangeStudio(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    country = SelectField("Country", choices=countries)
    creation_date = DateField("Creation Date")
    submit = SubmitField("Confirm change")

    def validate(self):
        name = self.name.data.strip()
        if self.creation_date.data != None and self.creation_date.data >= datetime.datetime.strptime(today, "%d.%m.%Y").date():
            flash("Date must be in the past")
            return False
        if len(name) < 1:
            # self.name.errors.append('Please enter user name')
            flash('Please enter user name')
            return False
        elif len(name) > 20 or len(name) < 5:
            # self.name.errors.append("Nazwa uzytkownika powinna mieć od 5 do 20 znaków")
            flash("Studio name must be between 5-20 characters")
            return False
        if self.country.data == '-':
            self.country.data = None
        return True

class AddNews(FlaskForm):
    title = StringField("Title", validators=[DataRequired(),Length(max=30)])
    content = StringField("Content", validators=[Length(min=30)], render_kw={"rows": 15}, widget=TextArea())
    submit = SubmitField("Add news")

    def validate(self):
        self.content.data = self.content.data.strip()
        return True

class EditNews(FlaskForm):
    title = StringField("Title", validators=[DataRequired(),Length(max=30)])
    content = StringField("Content", validators=[Length(min=30)], render_kw={"rows": 15}, widget=TextArea())
    submit = SubmitField("Edit")
    
    def validate(self):
        self.content.data = self.content.data.strip()
        return True