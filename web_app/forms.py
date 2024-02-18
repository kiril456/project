from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, TextAreaField, IntegerField, FileField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from web_app.modules import User
from flask_wtf.file import FileRequired


class RegisterForm(FlaskForm):
    name = StringField('Name: ', validators=[DataRequired(), Length(min=2, max=15)])
    email = EmailField('Email: ', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired(), Length(min=4)])
    password_confirm = PasswordField("Confrim Password: ", validators=[EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_name(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists! Please try a different username')
    
    def validate_email(self, email_address_to_check):
        email_address = User.query.filter_by(email=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('Email already exists! Please try a different email')
    
    
class LoginForm(FlaskForm):
    name = StringField('Name: ', validators=[DataRequired(), Length(min=2, max=15)])
    password = PasswordField('Password:', validators=[DataRequired(), Length(min=4)])
    submit = SubmitField('Sign In')
    

class ItemForm(FlaskForm):
    description = TextAreaField("Description of item", validators=[DataRequired()])
    price = IntegerField("Price of item", validators=[DataRequired()])
    image = FileField("Image of item", validators=[FileRequired()])
    submit = SubmitField("Send")
    
    
class BuyForm(FlaskForm):
    name = StringField('name')
    submit = SubmitField("Buy")
    
    
class CommentForm(FlaskForm):
    comment = TextAreaField("Comment", validators=[DataRequired()])
    submit = SubmitField("Post")
    
    
class ChangeProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=15)])
    password = PasswordField('Password:', validators=[DataRequired(), Length(min=4)])
    password_confirm = PasswordField("Confrim Password: ", validators=[EqualTo('password')])
    submit = SubmitField("Save")
    

class DonateForm(FlaskForm):
    cash = IntegerField('Cash', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Donate')
    