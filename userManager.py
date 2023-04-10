
USERS = []


class User():
    def __init__(self, username, password) -> None:
        self.username = username
        self.password = password
        self.logged_in = False

    def __str__(self) -> str:
        return f'Username: {self.username} Password: {self.password}'


def addUser(username, password):
    if validateNonExistingUser(username):
        newUser = User(username=username, password=password)
        USERS.append(newUser)
        return newUser
    else:
        return None


def getUser(username):
    for user in USERS:
        if user.username == username:
            return user
    return None


def validateNonExistingUser(username):
    if getUser(username):
        return False
    return True


def authenticate(username, password):
    user = getUser(username)
    if user != None:
        if user.password == password:
            user.logged_in = True
            return True
    return False
