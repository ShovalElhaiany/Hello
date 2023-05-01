from flask_wtf import Form
from wtforms import EmailField, IntegerField, StringField, HiddenField


class StudentForm(Form):
    id = HiddenField()
    firstName = StringField(label='First Name: ')
    lastName = StringField(label='Last Name: ')
    email = EmailField(label='Email: ')
    age = IntegerField(label='Age: ')
    phone = StringField(label='Phone Number: ')


class CourseForm(Form):
    id = HiddenField()
    name = StringField(label='Course name')

class LanguageForm(Form):
    id = HiddenField()
    name = StringField(label='Language name')
