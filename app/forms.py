from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User
from flask_login import current_user

#every class in app.forms is used to create web forms on different pages

#test form, if still here delete
class TestForm(FlaskForm):
    username2 = StringField('Username', validators=[DataRequired()])
    submit2 = SubmitField('Submit')

#form to allow admins to delete users
class DeleteUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Delete User')

#form to allow users to login
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

#form to register new users
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
            'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    #custom validator to ensure username is not duplicated
    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    #same as other custom validator
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        print(user)
        if user is not None:
            raise ValidationError('Please use a different email address.')

#form that allows users to edit their profiles
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    #seeing as this form needs to have custom default values this __init__ function is needed
    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    #same as other custom validators
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

#form that allows users to log games
class UpdateScoreForm(FlaskForm):
    winner = StringField('Winner Username', validators=[DataRequired()])
    loser = StringField('Loser Username', validators=[DataRequired()])
    submit = SubmitField('Submit')

    #i couldnt actually get these to work, so i ended up using a different approach, but i left these here in case i ever wanted to fix them
    def validate_winner(self, winner):
        user = User.query.filter_by(username=winner.data)
        if user is None:
            raise ValidationError('Winner name not found in database.')

    def validate_loser(self, loser):
        user = User.query.filter_by(username=loser.data)
        if user is None:
            raise ValidationError('Loser name not found in database.')