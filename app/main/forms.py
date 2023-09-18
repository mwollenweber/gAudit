'''
app/auth/forms.py

Copyright Insomniac Technology 2015


'''


#from flask.ext import Form
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateTimeField
from wtforms.validators import Required, Email, Length, Regexp, EqualTo
from wtforms import ValidationError
#from app.models import User, db


'''
class LoginForm(Form):
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField("Login")

    def get_user(self):
        return db.session.query(User).filter_by(email=self.email.data).first()

'''


class emailRetentionForm(Form):
    emailAddress = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    beginDate = DateTimeField()
    endDate = DateTimeField()
    query = StringField()
    includeDeleted = BooleanField()
    headersOnly = BooleanField()
    submit = SubmitField("Retain Email")

