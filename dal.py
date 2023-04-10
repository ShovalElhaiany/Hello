studentList = []


def addStudent(student):
    studentObj = getStudentByEmail(student['email'])
    if studentObj:
        removeStudent(studentObj)
    studentList.append(student)


def getStudentByEmail(email):
    for student in studentList:
        if student['email'] == email:
            return student
    return None


def removeStudent(student):
    studentList.remove(student)
