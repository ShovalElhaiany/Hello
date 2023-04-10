from flask import Flask, url_for, request, render_template, redirect, make_response, session, flash
from forms import StudentForm
import userManager
import dal
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from flask_restful import Api, Resource

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


class Names(Resource):
    def get(self):
        return fake_database

    def post(self):
        data = request.json
        nameId = len(fake_database.keys())+1
        fake_database[nameId] = {'name': data['name']}
        return fake_database
    
    


class Name(Resource):
    def get(self, pk):
        return fake_database[pk]
    
    def put(self):
        data = request.json


class Student(db.Model):
    id = db.Column('student_id', db.Integer, primary_key=True)
    firstName = db.Column(db.String(100))
    lastName = db.Column(db.String(100))
    email = db.Column(db.String(100))
    age = db.Column(db.Integer)
    phone = db.Column(db.String(100))
    courses = db.relationship('Course', backref='student', lazy=True)

    def __init__(self, firstName, lastName, email, age, phone) -> None:
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.age = age
        self.phone = phone


class Course(db.Model):
    id = db.Column('course_id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    student_id = db.Column(
        db.Integer, db.ForeignKey('student.student_id'), nullable=False)

    def __init__(self, name) -> None:
        self.name = name


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
    return url_for('hi', name='Shoval')


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


@app.route('/studentsingup', methods=['GET', 'POST'])
def studentSingup():
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
        student = Student(studentForm['firstName'],
                          studentForm['lastName'],
                          studentForm['email'],
                          studentForm['age'],
                          studentForm['phone'])

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
        student = request.args  # GET
        form = StudentForm(student)
    return render_template('student.html', form=form)


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
def deleteStudent(id):
    """Gust if I want to use 'Hidden Input'"""
    # id = request.form['id']

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
        Student.email.endswith(f'%{emailExt}%')).one_or_404()

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


"""A way to create separate URLS for functions"""
# @app.add_url_rule('/', 'hello', hello)
# @app.add_url_rule('/register', 'register', register, ['GET', 'POST'])

"""create db tables"""
# db.create_all()

app.secret_key = 'flaskey'
api.add_resource(Names, '/names')
api.add_resource(Name, '/name/<int:pk>')

if __name__ == '__main__':
    app.run(debug=True)
