class AccountInfo:
    username = None
    login = None
    password = None

    def __init__(self, username_, login_, password_):
        self.username = username_
        self.login = login_
        self.password = password_
    
    def getUsername(self):
        return self.username

    def getLogin(self):
        return self.login
    
    def getPassword(self):
        return self.password