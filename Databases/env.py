from flask_mysqldb import MySQL

class Connector :
    def __init__(self, localhost, user, password, database, app):
        self.localhost = localhost
        self.user = user
        self.password = password
        self.database = database
        self.app = app
    
    def ConnexionDatabase(self) :
        self.app.config["MYSQL_HOST"] = self.localhost
        self.app.config['MYSQL_USER'] = self.user
        self.app.config['MYSQL_PORT'] = 3306
        self.app.config['MYSQL_PASSWORD'] = self.password
        self.app.config['MYSQL_DB'] = self.database

        mysql = MySQL(self.app)
        return mysql