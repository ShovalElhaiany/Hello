from flask_wtf import Form
from wtforms import EmailField, IntegerField, StringField, HiddenField


class StudentForm(Form):
    id = HiddenField()
    firstName = StringField(label='First Name: ')
    lastName = StringField(label='Last Name: ')
    email = EmailField(label='Email: ')
    age = IntegerField(label='Age: ')
    phone = StringField(label='Phone Number: ')
