import sqlite3

class DBHelper:
    def __init__(self, dbname='random_coffee.sqlite'):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        sql = "CREATE TABLE IF NOT EXISTS users (username text PRIMARY KEY)"
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()

    def add_user(self, username):
        sql = "INSERT INTO users VALUES (?)"
        args = (username, )
        self.conn.execute(sql, args)
        self.conn.commit()
    
    def delete_user(self, username):
        sql = 'DELETE FROM users WHERE username = (?)'
        args = (username,)
        self.conn.execute(sql, args)
        self.conn.commit()

    def get_users(self):
        sql = 'SELECT * FROM users'
        return [x[0] for x in self.conn.execute(sql)]