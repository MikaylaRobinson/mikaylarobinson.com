from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")])
    secret_pass = PasswordField("Entry Code", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Please use a different email address.")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")

class NewBlogForm(FlaskForm):
    keyword = StringField("Keyword", validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired()])
    tools_used = StringField("Tools Used", validators=[DataRequired()])
    content = TextAreaField("Content")
    submit = SubmitField("Register")

class NewSideProjectForm(FlaskForm):
    keyword = StringField("Keyword", validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired()])
    tools_used = StringField("Tools Used", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Register")