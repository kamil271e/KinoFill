from config import *
from utils import *


class RegisterForm(FlaskForm):
    login = StringField("Login",validators=[DataRequired(), Length(5, 16)], render_kw={"placeholder": "Enter 5 to 16 characters"})
    password = PasswordField("Password", validators=[DataRequired(), Length(5, 16)], render_kw={"placeholder": "Enter 5 to 16 characters"})
    password_confirm = PasswordField("Confirm password", validators=[DataRequired(), Length(5, 16)]) #, EqualTo('password', message="Passwords must match")])
    role = SelectField("Role", choices=["Viewer", "Journalist", "Studio"])
    user_desc = StringField("Profile description", widget=TextArea())
    viewer_role = SelectField("Account type", choices=["Private", "Public"])
    name = StringField("Name")
    submit = SubmitField("Register")

    def validate(self):
        # self.login.data = " ".join(self.login.data.split())
        self.user_desc.data = " ".join(self.user_desc.data.split())
        if self.password.data != self.password_confirm.data:
            flash("Passwords must match")
            return False
        if self.role.data != "Viewer" or self.viewer_role.data == "Public":
            self.name.data = " ".join(self.name.data.split())
            if len(self.name.data) < 1:
                # self.name.errors.append('Please enter user name')
                flash('Please enter user name')
                return False
            elif self.role.data == "Studio" and len(self.name.data) > 30 and len(self.name.data) < 5:
                flash("Studio name should have between 5 and 30 characters")
                return False
            elif self.role.data != "Studio" and len(self.name.data) > 20 or len(self.name.data) < 5:
                flash("Username should have between 5 and 20 characters")
                return False
        if len(self.user_desc.data) > 200:
            flash("User description should not exceed 200 characters")
            return False
        return True


class AddMovie(FlaskForm):
    name = StringField("Title", render_kw={"placeholder": "Enter max 30 characters"})
    creation_year = SelectField('Creation year', coerce=int, choices=range(int(today[6:]), int(today[6:]) - 100, -1))
    length = StringField("Length (in minutes)")
    director = SelectField("Director")
    studio = SelectField("Studio")  # Only for admin to choose
    choose_studio = False
    submit = SubmitField("Add movie")
    redirect_add_director = SubmitField("Add director")

    def __init__(self, choose_studio, *args, **kwargs):
        self.choose_studio = choose_studio
        super(AddMovie, self).__init__(*args, **kwargs)

    def validate(self):
        self.name.data = " ".join(self.name.data.split())
        self.length.data = " ".join(self.length.data.split())
        if self.redirect_add_director.data:
            return True
        if not self.name.data:
            flash("Please enter movie name")
            return False
        if len(self.name.data) < 1:
            flash("Please enter valid movie title")
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
        if len(self.name.data) > 30:
            flash("The name must not exceeded 30 characters. Please try again")
            return False

        return True


class AddDirector(FlaskForm):
    firstname = StringField("First name", validators=[DataRequired()], render_kw={"placeholder": "Enter 2 to 20 characters"})
    surname = StringField("Surname", validators=[DataRequired()], render_kw={"placeholder": "Enter 2 to 20 characters"})
    birth_date = DateField("Birthdate",
                           validators=[DataRequired()])  # , format='%d.%m.%Y', validators=[DataRequired()])
    country = SelectField("Country", choices=countries)
    studio = SelectField("Studio")  # Only for admin to choose
    choose_studio = False
    submit = SubmitField("Add director")

    def __init__(self, choose_studio, *args, **kwargs):
        self.choose_studio = choose_studio
        super(AddDirector, self).__init__(*args, **kwargs)

    def validate(self):
        self.firstname.data = " ".join(self.firstname.data.split())
        self.surname.data = " ".join(self.surname.data.split())
        if nameInvalid(self.firstname.data) or nameInvalid(self.surname.data):
            flash("First name and surname cannot have any numbers or special characters")
            return False
        if self.birth_date.data is None:
            flash("Enter valid date")
            return False
        if self.birth_date.data >= datetime.datetime.strptime(today, "%d.%m.%Y").date():
            flash("Date needs to be from past")
            return False
        if len(self.firstname.data) < 2 or len(self.firstname.data) > 20:
            flash("Enter valid name")
            return False
        if len(self.surname.data) < 2 or len(self.surname.data) > 20:
            flash("Enter valid surname")
            return False
        if self.country.data == '-':
            self.country.data = None
        self.firstname.data = convertName(self.firstname.data)
        self.surname.data = convertName(self.surname.data)
        return True


class AddSeries(FlaskForm):
    name = StringField("Title", render_kw={"placeholder": "Enter max 30 characters"})
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
        self.name.data = " ".join(self.name.data.split())
        self.episodes.data = " ".join(self.episodes.data.split())
        if self.redirect_add_director.data:
            return True
        if not self.name.data:
            flash("Please enter series title")
            return False
        if len(self.name.data) < 1:
            flash("Please enter valid series name")
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
        if len(self.name.data) > 30:
            flash("Title is too long")
            return False
        if int(self.episodes.data) < 0:
            flash("Number of episodes cannot be negative")
            return False

        return True


class AddActor(FlaskForm):
    firstname = StringField("First name", validators=[DataRequired()], render_kw={"placeholder": "Enter 2 to 20 characters"})
    surname = StringField("Surname", validators=[DataRequired()], render_kw={"placeholder": "Enter 2 to 20 characters"})
    birth_date = DateField("Birthdate",
                           validators=[DataRequired()])  # , format='%d.%m.%Y', validators=[DataRequired()])
    country = SelectField("Country", choices=countries)
    studio = SelectField("Studio")
    choose_studio = False
    submit = SubmitField("Add actor")

    def __init__(self, choose_studio, *args, **kwargs):
        self.choose_studio = choose_studio
        super(AddActor, self).__init__(*args, **kwargs)

    def validate(self):
        self.firstname.data = " ".join(self.firstname.data.split())
        self.surname.data = " ".join(self.surname.data.split())
        if nameInvalid(self.firstname.data) or nameInvalid(self.surname.data):
            flash("First name and surname cannot have any numbers or special characters")
            return False
        if self.birth_date.data is None:
            flash("Enter valid date")
            return False
        if self.birth_date.data >= datetime.datetime.strptime(today, "%d.%m.%Y").date():
            flash("Date needs to be from past")
            return False
        if len(self.firstname.data) < 2 or len(self.firstname.data) > 20:
            flash("Enter valid name")
            return False
        if len(self.surname.data) < 2 or len(self.surname.data) > 20:
            flash("Enter valid surname")
            return False
        if self.country.data == '-':
            self.country.data = None
        self.firstname.data = convertName(self.firstname.data)
        self.surname.data = convertName(self.surname.data)
        return True


class ChangeStudio(FlaskForm):
    name = StringField("Name", validators=[DataRequired()], render_kw={"placeholder": "Enter 5 to 20 characters"})
    country = SelectField("Country", choices=countries)
    creation_date = DateField("Creation Date")
    submit = SubmitField("Confirm change")

    def validate(self):
        self.name.data = " ".join(self.name.data.split())
        if self.creation_date.data != None and self.creation_date.data >= datetime.datetime.strptime(today,"%d.%m.%Y").date():
            flash("Date must be in the past")
            return False
        if len(self.name.data) < 1:
            # self.name.errors.append('Please enter user name')
            flash('Please enter user name')
            return False
        elif len(self.name.data) > 20 or len(self.name.data) < 5:
            # self.name.errors.append("Nazwa uzytkownika powinna mieć od 5 do 20 znaków")
            flash("Studio name must be between 5-20 characters")
            return False
        if self.country.data == '-':
            self.country.data = None
        return True

class AddNews(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=30)], render_kw={"placeholder": "Enter max 30 characters"})
    content = StringField("Content", validators=[Length(min=30)], render_kw={"rows": 15}, widget=TextArea())
    submit = SubmitField("Add news")

    def validate(self):
        self.title.data = " ".join(self.title.data.split())
        self.content.data = " ".join(self.content.data.split())
        if len(self.content.data) > 2500:
            flash("News shouldn't be longer than 2500 characters")
            return False
        return True

class EditNews(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=30)], render_kw={"placeholder": "Enter max 30 characters"})
    content = StringField("Content", validators=[Length(min=30)], render_kw={"rows": 15}, widget=TextArea())
    submit = SubmitField("Edit")
    
    def validate(self):
        self.title.data = " ".join(self.title.data.split())
        self.content.data = " ".join(self.content.data.split())
        if len(self.content.data) > 2500:
            flash("News shouldn't be longer than 2500 characters")
            return False
        return True

class AddReview(FlaskForm):
    review_object_type = SelectField("Review object type", choices=["Movie", "Series", "Actor"])
    rate = SelectField("Rate", choices=["1", "2", "3", "4", "5"], default="3")
    content = StringField("Content (Optional)", widget=TextArea(), validators=[Length(max=30)])
    submit_m = SubmitField("Add Review")
    submit_s = SubmitField("Add Review")
    submit_a = SubmitField("Add Review")

    def validate(self):
        self.content.data = " ".join(self.content.data.split())
        return True


class AddReviewMovie(FlaskForm):
    rate = SelectField("Rate", choices=["1", "2", "3", "4", "5"], default="3")
    content = StringField("Content (Optional)", widget=TextArea(), validators=[Length(max=30)])
    submit = SubmitField("Add Review")

    def validate(self):
        self.content.data = " ".join(self.content.data.split())
        return True


class EditReview(FlaskForm):
    rate = SelectField("Rate", choices=["1", "2", "3", "4", "5"])
    content = StringField("Content (Optional)", widget=TextArea(), validators=[Length(max=30)])
    submit = SubmitField("Edit Review")

    def validate(self):
        self.content.data = " ".join(self.content.data.split())
        return True


class AddReviewSeries(AddReviewMovie):
    def __init__(self):
        super().__init__()


class AddReviewActor(AddReviewMovie):
    def __init__(self):
        super().__init__()


class ChangeMovie(AddMovie):
    submit = SubmitField("Confirm change")
    def __init__(self, choose_studio, *args, **kwargs):
        super().__init__(choose_studio, *args, **kwargs)


class ChangeSeries(FlaskForm):
    name = StringField("Title", render_kw={"placeholder": "Enter max 30 characters"})
    episodes = StringField("Number of episodes")
    seasons = StringField("Number of seasons")
    submit = SubmitField("Edit series")

    def validate(self):
        self.name.data = " ".join(self.name.data.split())
        self.episodes.data = " ".join(self.episodes.data.split())
        self.seasons.data = " ".join(self.seasons.data.split())
        if not self.name.data:
            flash("Please enter series title")
            return False
        if len(self.name.data) > 30:
            flash("Title is too long")
            return False
        if len(self.name.data) < 1:
            flash("Enter valid series title")
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
        if int(self.episodes.data) < 0:
            flash("Number of episodes cannot be negative")
            return False
        
        if not self.seasons.data:
            flash("Please enter number of seasons")
            return False
        if len(self.seasons.data) > 9:
            flash("There can't be that many seasons")
            return False
        try:
            self.seasons.data = int(self.seasons.data)
        except:
            flash("Number of seasons needs to be an integer")
            return False
        if int(self.seasons.data) < 0:
            flash("Number of episodes cannot be negative")
            return False
        if int(self.seasons.data) > int(self.episodes.data):
            flash("Number of seasons cannot be greater than number of episodes")
            return False

        return True


class ChangeActor(AddActor):
    submit = SubmitField("Confirm change")
    def __init__(self, choose_studio, *args, **kwargs):
        super().__init__(choose_studio, *args, **kwargs)


class ChangeDirector(AddDirector):
    submit = SubmitField("Confirm change")
    def __init__(self, choose_studio, *args, **kwargs):
        super().__init__(choose_studio, *args, **kwargs)


class ChangeJournalist(FlaskForm):
    nickname = StringField('Nickname', validators=[DataRequired()], render_kw={"placeholder": "Enter 5 to 20 characters"})
    firstname = StringField('First Name', render_kw={"placeholder": "Enter 2 to 20 characters"})
    surname = StringField('Surname', render_kw={"placeholder": "Enter 2 to 20 characters"})
    birth_date = DateField('Birth date')
    user_desc = StringField("Profile description", widget=TextArea())
    submit = SubmitField("Confirm change")

    def validate(self):
        self.firstname.data = " ".join(self.firstname.data.split())
        self.surname.data = " ".join(self.surname.data.split())
        self.nickname.data = " ".join(self.nickname.data.split())
        self.user_desc.data = " ".join(self.user_desc.data.split())

        if self.birth_date.data != None and self.birth_date.data >= datetime.datetime.strptime(today,"%d.%m.%Y").date():
            flash("Date must be in the past")
            return False
        if str(self.firstname.data) != "":
            if nameInvalid(self.firstname.data):
                flash("First name cannot have any numbers or special characters")
                return False
            if len(self.firstname.data) < 2 or len(self.firstname.data) > 20:
                flash("Enter valid firstname")
                return False 
        if str(self.surname.data) != "":
            if nameInvalid(self.surname.data):
                flash("Surname cannot have any numbers or special characters")
                return False
            if len(self.surname.data) < 2 or len(self.surname.data) > 20:
                flash("Enter valid surname")
                return False 
        if len(self.nickname.data) > 20 or len(self.nickname.data) < 5:
            flash("Nickname should have between 5 and 20 characters")
            return False
        if len(self.user_desc.data) > 200:
            flash("User description should not exceed 200 characters")
            return False
        
        return True

class ChangePublicViewer(FlaskForm):
    nickname = StringField('Nickname', validators=[DataRequired()], render_kw={"placeholder": "Enter 5 to 20 characters"})
    user_desc = StringField("Profile description", widget=TextArea())
    viewer_role = SelectField("Account type", choices=["Public", "Private"])
    submit = SubmitField("Confirm changes")
    
    def validate(self):
        self.nickname.data = " ".join(self.nickname.data.split())
        self.user_desc.data = " ".join(self.user_desc.data.split())
        if self.viewer_role.data == 'Public':
            if len(self.nickname.data) > 20 or len(self.nickname.data) < 5:
                flash("Nickname should have between 5 and 20 characters")
                return False
            if len(self.user_desc.data) > 200:
                flash("User description should not exceed 200 characters")
                return False
        
        return True
