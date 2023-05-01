from flask import Flask, url_for, request, render_template, redirect, make_response, session, flash
from forms import StudentForm, CourseForm, LanguageForm
import userManager
import dal
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from flask_restful import Api, Resource, fields, marshal_with
import json

app = Flask('__name__')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///collage.sqlite3'
db = SQLAlchemy(app=app)
app.app_context().push()
api = Api(app)


fake_database = {
    1: {'name': "shalev"},
    2: {'name': "shoval"},
    3: {'name': "shoham"},
    4: {'name': "amit"},
}


def readFromDB():
    global fake_database

    with open('jNames.txt', 'r') as reader:
        lines = reader.readlines()
        for line in lines:
            key = int(line[0])
            val = line[2:-1].replace('\'', '\"')
            fake_database[key] = json.loads(val)


def writeToDB():
    with open('jNames.txt', 'w') as writer:
        for key, val in fake_database.items():
            writer.write(f'{key}:{val}\n')


def updateDB(key, val):
    with open('jNames.txt', 'r') as reader:
        lines = reader.readlines()
    with open('jNames.txt', 'w') as writer:
        for line in lines:
            if line[0] == str(key):
                writer.write(f'{key}:{val}\n')
            else:
                writer.write(line)


def deleteFromDB(key):
    with open('jNames.txt', 'r') as reader:
        lines = reader.readlines()
    with open('jNames.txt', 'w') as writer:
        for line in lines:
            if line[0] != str(key):
                writer.write(line)

# def readFormDB():
#     global fake_database
#     with open('nameDB.txt', 'r') as reader:
#         data = reader.read()
#         fake_database = json.loads(data)


# def writeToDB():
#     with open('nameDB.txt', 'w') as writer:
#         writer.write(json.dumps(fake_database))


def generateId():
    ids = fake_database.keys()
    maxId = max(ids)
    return int(maxId)+1


class Names(Resource):
    def get(self):
        return fake_database

    def post(self):
        data = request.json
        nameId = generateId()
        fake_database[nameId] = {'name': data['name']}
        writeToDB()
        return fake_database


class Name(Resource):
    def get(self, pk):
        return fake_database[pk]

    def put(self, pk):
        data = request.json
        fake_database[pk]['name'] = data['name']
        # writeToDB()
        updateDB(pk, fake_database[pk])
        return fake_database[pk]

    def delete(self, pk):
        fake_database.pop(pk)
        # writeToDB()
        deleteFromDB(pk)
        return fake_database


courses = db.Table('Courses',
                   db.Column('student_id', db.Integer, db.ForeignKey('student.student_id'), primary_key=True),
                   db.Column('course_id', db.Integer, db.ForeignKey('course.course_id'), primary_key=True))

languages = db.Table('Languages',
                     db.Column('course_id', db.Integer, db.ForeignKey('course.course_id'), primary_key=True),
                     db.Column('language_id', db.Integer, db.ForeignKey('language.language_id'), primary_key=True))

languageTostudents = db.Table('LanguageTostudents',
                     db.Column('student_id', db.Integer, db.ForeignKey('student.student_id'), primary_key=True),
                     db.Column('language_id', db.Integer, db.ForeignKey('language.language_id'), primary_key=True))

student_fields = {
    'id': fields.Integer,
    'firstName': fields.String,
    'lastName': fields.String,
    'email': fields.String,
    'age': fields.Integer,
    'phone': fields.String,
}


class Student(db.Model):
    id = db.Column('student_id', db.Integer, primary_key=True)
    firstName = db.Column(db.String(100))
    lastName = db.Column(db.String(100))
    email = db.Column(db.String(100))
    age = db.Column(db.Integer)
    phone = db.Column(db.String(100))
    """One to Many / One to One(uselist=False)"""
    # courses = db.relationship('Course', backref='student', lazy=True, uselist=False)
    courses = db.relationship('Course', secondary=courses, backref=db.backref('students', lazy=True))
    language_id = db.relationship('Language', secondary=languageTostudents, backref=db.backref('students', lazy=True))

    def __init__(self, firstName, lastName, email, age, phone, courses=None, language=None) -> None:
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.age = age
        self.phone = phone
        self.courses = courses
        self.language = language

class Course(db.Model):
    id = db.Column('course_id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    # student_id = db.Column(
    #     db.Integer, db.ForeignKey('student.student_id'), nullable=False)#uselist=False
    languages = db.relationship(
        'Language', secondary=languages, backref=db.backref('languages', lazy=True))

    def __init__(self, name, language=None) -> None:
        self.name = name
        self.language = language


class Language(db.Model):
    id = db.Column('language_id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __init__(self, name) -> None:
        self.name = name

    def __str__(self) -> str:
        return self.name


class StudentDetails(Resource):
    @marshal_with(student_fields)
    def get(self, pk):
        student = Student.query.get(pk)
        return student


class Studentlist(Resource):
    @marshal_with(student_fields)
    def get(self):
        students = Student.query.all()
        return students

    def post(self):
        data = request.json
        newStudent = Student(firstName=data['firstName'], lastName=data['lastName'],
                             email=data['email'], age=data['age'], phone=data['phone'], )
        db.session.add(newStudent)
        db.session.commit()
        return redirect(url_for('Studentlist'))





@app.route('/', methods=['GET'])
def hello():
    return render_template('hello.html')


@app.route('/hi/<string:name>')
def hi(name):
    if 'username' in session.keys():
        return render_template('hello.html', name=name)
    return 'NOT AUTHORIZED 401'


@app.route('/sayhello')
def sayHello():
    return redirect(url_for('hi', name='Shoval'))


@app.route('/loginn', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session['username'] = username
        flash(f'{username} you are now logged in', 'info')
        flash('Please remember to log out', 'warning')
        return redirect(url_for('hi', name=username))

    """If we pull information from the DB in this way, the code must be protected with Try and Except"""
    # try:
    #     username = request.args['username', '']
    #     password = request.args['password', '']
    # except:

    """Planting cookies for the user"""
    #     username = ''
    # username = request.args.get('username', '')
    # password = request.args.get('password', '')
    # response = make_response(
    #     f'from GET:user name is {username} password is: {password}:')
    # response.set_cookie('username', username)
    # return response
    return render_template('login.html')


@app.get('/login')
def login_get():
    return render_template('login.html')


@app.post('/login_user')
def login_post():
    username = request.form['username']
    password = request.form['password']
    if userManager.authenticate(username, password):
        session['username'] = username
        return redirect(url_for('hi', name=username))
    return 'Bed credentials'


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = userManager.addUser(username=username, password=password)
        if user != None:
            session['username'] = username
            return redirect(url_for('hi', name=username))
    return render_template('register.html')


@app.route('/grades', methods=['GET', 'POST'])
def grades():
    if request.method == 'POST':
        grades = request.form
        username = request.cookies['username']
        return render_template('grades.html', grades=grades)
    else:
        grades = request.args
        username = request.cookies['username']
        return render_template('gradesForm.html', grades=grades, username=username)


@app.route('/student/<int:id>')
def student(id):
    """Using DAL"""
    # student = dal.getStudentByEmail(email)

    student = Student.query.get(id)
    form = StudentForm(obj=student)
    return render_template('student.html', form=form)


@app.route('/studentsignup', methods=['GET', 'POST'])
def studentSignup():
    """Pulling information from the DB"""
    # firstname = request.args.get('firstName', '')
    # lastname = request.args.get('lastName', '')
    # student = {'firstname': firstname,
    #            'lastname': lastname}

    if request.method == 'POST':

        """Using DAL"""
        # student = request.form  # POST
        # dal.addStudent(student=student)

        studentForm = request.form  # POST
        course_ids = [int(id) for id in studentForm.getlist('courses')]
        language_ids = [int(id) for id in studentForm.getlist('languages')]
        student = Student(studentForm['firstName'],
                          studentForm['lastName'],
                          studentForm['email'],
                          studentForm['age'],
                          studentForm['phone'])
        courses = Course.query.filter(Course.id.in_(course_ids)).all()
        languages = Language.query.filter(Language.id.in_(language_ids)).all()
        student.courses.extend(courses)
        student.language_id.extend(languages)
        db.session.add(student)
        db.session.commit()

        """Adding a course model to the student table"""
        # course = Course(name="test course")
        # student.courses.append(course)
        # db.session.add(student)
        # db.session.commit()
        """Use of sqlite3 and pulling information from DB using SQL"""
        # with sqlite3.connect('collage.sqlite3') as con:
        #     cur = con.cursor()
        #     cur.execute('insert into student (firstName, lastName, email, age, phone) values (?, ?, ?, ?, ?);',(student))
        #     con.commit()
        # return render_template('studentList.html', students=rows)

        return redirect(url_for('students'))
    else:
        # student = request.args  # GET
        # form = StudentForm(student)

        courses = Course.query.all()
        form = StudentForm()
        languages = Language.query.all()
    return render_template('student.html', form=form, courses=courses, languages=languages)


"""Another response"""
# return render_template('helloStudent.html', student=student)


@app.route('/studentDtails/<int:id>', methods=['GET', 'POST', 'DELETE'])
def studentDetails(id):
    student = Student.query.get_or_404(id)

    """Filter information by column"""
    # student = Student.filter_by(StudentForm.email).all()

    if request.method == 'POST':
        form = request.form
        student.firstName = form['firstName']
        student.lastName = form['lastName']
        student.email = form['email']
        student.age = form['age']
        student.phone = form['phone']
        db.session.commit()
        return redirect(url_for('students'))
    return render_template('studentUpdate.html', form=StudentForm(obj=student))


@app.route('/deleteStudent/<int:id>', methods=['POST'])
def deleteStudent():
    """If I dont want to use 'Hidden Input'"""
# def deleteStudent(id):
    """just if I want to use 'Hidden Input'"""
    id = request.form['id']

    student = Student.query.get(id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('students'))


@app.route('/deleteStudents', methods=['POST'])
def deleteStudents():
    ids = request.form.getlist('id')
    for id in ids:
        student = Student.query.get(id)
        db.session.delete(student)
    db.session.commit()
    return redirect(url_for('students'))


@app.route('/searchByName')
def searchByName():
    name = request.args.get('name', '')
    students = Student.query.filter(Student.firstName.like(
        f'%{name}%') | Student.lastName.like(f'%{name}%')).limit(5).all()
    return render_template('studentList.html', students=students)


@app.route('/searchByMailType')
def searchByMailType():
    emailExt = request.args.get('emailExt', '')
    students = Student.query.filter(
        Student.email.endswith(f'%{emailExt}%')).all()
    """One or 404"""
    # students = Student.query.filter(Student.email.endswith(f'%{emailExt}%')).one_or_404()

    """Retrieving information or 404"""
    # students = Student.query.get_or_404(id)

    return render_template('studentList.html', students=students)


@app.route('/students')
def students():
    # students = dal.studentList
    students = Student.query.all()
    return render_template('studentList.html', students=students)


"""Use of sqlite3 and pulling information from DB using SQL"""
# with sqlite3.connect('./insrance/collage.sqlite3') as con:
#     cur=con.cursor()
#     cur.execute('select * from student;')
#     rows = cur.fetchall()
# return render_template('studentList.html', students=rows)


@app.route('/logout')
def logout():
    session.pop('username', '')
    return redirect(url_for('login_get'))


@app.route('/add_course')
def add_course():
    form = CourseForm()
    languages = Language.query.all()
    return render_template('course.html', form=form, languages=languages)


@app.route('/course/<int:id>', methods=['GET', 'POST'])
def course(id):
    course = Course.query.get(id)
    if request.method == 'GET':
        form = CourseForm(obj=course)
        return render_template('course.html', form=form)
    else:
        course.name = request.form['name']
        db.session.commit()
        return redirect(url_for('courses'))


@app.route('/deleteCourses', methods=['POST'])
def deleteCourses():
    ids = request.form.getlist('id')
    coursesToDelete = Course.query.filter(
        Course.id.in_([int(id) for id in ids]))
    for course in coursesToDelete:
        db.session.delete(course)
    db.session.commit()
    return redirect(url_for('courses'))


@app.route('/courses', methods=['GET', 'POST'])
def courses():
    if request.method == 'POST':
        courseForm = request.form
        course = Course(name=courseForm['name'],
                        language=courseForm.getlist('languages'))
        language_ids = [int(id) for id in course.language]
        languages = Language.query.filter(Language.id.in_(language_ids)).all()
        course.languages.extend(languages)
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('courses'))
    else:
        courses = Course.query.all()
        return render_template('courses.html', courses=courses)


@app.route('/languages', methods=['GET', 'POST'])
def languages():
    languages = Language.query.all()
    return render_template('languages.html', languages=languages)


@app.route('/language/<int:id>', methods=['GET', 'POST'])
def language(id):
    language = Language.query.get(id)
    if request.method == 'GET':
        form = LanguageForm(obj=language)
        return render_template('language.html', form=form)
    else:
        language.name = request.form['name']
        db.session.commit()
        return redirect(url_for('languages'))


@app.route('/add_language')
def add_language():
    form = LanguageForm()
    return render_template('language.html', form=form)


@app.route('/deleteLanguages', methods=['POST'])
def deleteLanguages():
    ids = request.form.getlist('id')
    languagesToDelete = Language.query.filter(
        Language.id.in_([int(id) for id in ids]))
    for language in languagesToDelete:
        db.session.delete(language)
    db.session.commit()
    return redirect(url_for('languages'))


"""A way to create separate URLS for functions"""
# @app.add_url_rule('/', 'hello', hello)
# @app.add_url_rule('/register', 'register', register, ['GET', 'POST'])

"""create db tables"""
# db.create_all()

app.app_context().push()
app.secret_key = 'flaskey'
api.add_resource(Names, '/names')
api.add_resource(Name, '/name/<int:pk>')
api.add_resource(Studentlist, '/api/students')
api.add_resource(StudentDetails, '/api/student/<int:pk>')
# writeToDB()
readFromDB()

if __name__ == '__main__':
    app.run(debug=True)
